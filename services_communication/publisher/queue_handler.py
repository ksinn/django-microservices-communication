import logging
import select
import json
import time

try:
    import psycopg2
except ImportError:
    pass

from django.conf import settings

from services_communication import publishing_backend
from services_communication.settings import communication_settings
from services_communication.broker import BlockedPublisher


logger = logging.getLogger('services_communication.publisher.process')


class SyncPoolingPublisherQueueHandler:

    def __init__(self, app_id=None, broker_connection_parameters=None, exchanges=None, **kwargs):
        self.mq = BlockedPublisher(
            app_id=app_id,
            broker_connection_parameters=broker_connection_parameters,
            exchanges=exchanges,
        )

    def run(self):
        while True:
            for message in publishing_backend.get_messages_for_send_to_broker():
                if message.is_new_style:
                    self.mq.publish(
                        exchange=message.exchange,
                        routing_key=message.routing_key,
                        body=json.dumps(message.body),
                    )
                else:
                    self.mq.publish(
                        exchange=message.exchange,
                        routing_key=message.routing_key,
                        body=json.dumps({
                            'eventId': message.id,
                            'eventTime': message.event_time.isoformat(),
                            'eventType': message.event_type,
                            'aggregate': message.aggregate,
                            'payload': message.payload,

                        }),
                    )
                publishing_backend.delete(message)
            time.sleep(1)

class ListenPublisherQueueHandler:

    notification_select_timeout = 15

    def __init__(self, app_id=None, broker_connection_parameters=None, exchanges=None, **kwargs):
        assert psycopg2, 'ListenPublisher work by NOTIFY/LISTEN and available only for PostgreSQL and required "psycopg2"'
        assert not communication_settings.PUBLISHER_FUTURE_EVENT_ENABLE, 'ListenPublisher can\'t handel with future event yet'

        db_settings = settings.DATABASES[publishing_backend.get_db_alias()]
        if "postgresql" not in db_settings["ENGINE"]:
            raise Exception("ListenPublisherQueueHandler available only if PublishedEventQueue model use PostgreSQL databases.")
        db_dsn = build_settings_to_url(db_settings)

        scheme, tabel = publishing_backend.get_scheme_and_tabel_name()
        self.chanel_name = f"{scheme}_eventqueued"

        self.mq = BlockedPublisher(
            app_id=app_id,
            broker_connection_parameters=broker_connection_parameters,
            exchanges=exchanges,
        )

        self.conn = psycopg2.connect(db_dsn, **{'async': 1})
        self.wait()

    def publish_messages_from_queue(self):
        for message in publishing_backend.get_messages_for_send_to_broker():
            if message.is_new_style:
                self.mq.publish(
                    exchange=message.exchange,
                    routing_key=message.routing_key,
                    body=json.dumps(message.body),
                )
            else:
                self.mq.publish(
                    exchange=message.exchange,
                    routing_key=message.routing_key,
                    body=json.dumps({
                        'eventId': message.id,
                        'eventTime': message.event_time.isoformat(),
                        'eventType': message.event_type,
                        'aggregate': message.aggregate,
                        'payload': message.payload,

                    }),
                )
            publishing_backend.delete(message)

    def run(self):

        logger.info('Chane name for listen pg notification: {}'.format(self.chanel_name))

        with self.conn.cursor() as curs:
            curs.execute(f"LISTEN {self.chanel_name};")
            if not self.wait(socket_timeout=5):
                raise psycopg2.OperationalError('Set listen statement execution soket await timeout')
            logger.debug('Listener set')

        self.publish_messages_from_queue()

        while True:
            timeout_counter = 0
            while timeout_counter < 60:
                has_notifications = self.await_notifies()
                if has_notifications:
                    timeout_counter = 0
                    self.publish_messages_from_queue()
                else:
                    timeout_counter = timeout_counter + self.notification_select_timeout

            logger.debug('Start connection health status')
            if not self.is_connection_healthy():
                logger.error('Response do not received in timeout. Connection unhealthy')
                self.conn.close()
                raise psycopg2.OperationalError('Connection unhealthy!')
            logger.debug('Connection healthy')

    def await_notifies(self):
        logger.debug("Await notifies from DB...")
        if select.select([self.conn], [], [], self.notification_select_timeout) == ([], [], []):
            return False
        else:
            self.conn.poll()
            logger.debug("Receive %d notifications from DB", len(self.conn.notifies))
            self.conn.notifies.clear()
            return True

    def is_connection_healthy(self, timeout=None):
        if not timeout:
            timeout = 5

        with self.conn.cursor() as curs:
            curs.execute("select 1;")
            if not self.wait(socket_timeout=timeout):
                return False
            return True

    def wait(self, socket_timeout=None):
        timeout_pass = False
        last_state = None
        while True:
            state = self.conn.poll()

            if last_state != state:
                timeout_pass = False

            if timeout_pass:
                return False

            if state == psycopg2.extensions.POLL_OK:
                break
            elif state == psycopg2.extensions.POLL_WRITE:
                if select.select([], [self.conn.fileno()], [], socket_timeout) == ([], [], []):
                    timeout_pass = True
            elif state == psycopg2.extensions.POLL_READ:
                if select.select([self.conn.fileno()], [], [], socket_timeout) == ([], [], []):
                    timeout_pass = True
            else:
                raise psycopg2.OperationalError("poll() returned %s" % state)
            last_state = state

        return True


def build_settings_to_url(db_settings):
    DATABASE_URL = f"postgresql://{db_settings['USER']}:{db_settings['PASSWORD']}@{db_settings['HOST']}:{db_settings['PORT']}/{db_settings['NAME']}"
    return DATABASE_URL