import logging
import random
import time

import pika
from pika.exceptions import AMQPConnectionError
from pika.exchange_type import ExchangeType

from services_communication.error import MessageNotConsumed
from services_communication.settings import communication_settings
from services_communication.types import Exchange

logger_consumer = logging.getLogger('services_communication.consumer')
logger_publisher = logging.getLogger('services_communication.publisher')


class BlockedMixin:

    def _declare_queue(self, channel):
        channel.queue_declare(self._queue, durable=True)

    def _declare_exchanges(self, channel):
        for exchange in self._exchanges:
            channel.exchange_declare(exchange.name, exchange_type=exchange.type, durable=True)

    def _declare_binds(self, channel):
        for bind in self._binds:
            channel.queue_bind(self._queue, bind.exchange, routing_key=bind.routing_key)


class BlockedConsumer(BlockedMixin):

    def __init__(self,
                 broker_connection_parameters=None,
                 queue=None,
                 exchanges=None,
                 binds=None,
                 on_message_callback=None,
                 ignore_callback_error=False,
                 **kwargs):
        logger_consumer.info('Init {} with callback {}'.format(type(self).__name__, on_message_callback))
        self._broker_connection_parameters = broker_connection_parameters
        self._queue = queue
        self._exchanges = exchanges
        self._binds = binds
        self._on_message_callback = on_message_callback
        self._ignore_callback_error = ignore_callback_error

    def on_message(self, channel, method_frame, header_frame, body):
        logger_consumer.debug('Received message (dt:{}) from exchange {} with key {}'.format(method_frame.delivery_tag,
                                                                                             method_frame.exchange,
                                                                                             method_frame.routing_key))
        try:
            communication_settings.CORRELATION_ID_HELPER.set_correlation_id(header_frame.correlation_id)
            self._on_message_callback(method_frame, header_frame, body)
        except MessageNotConsumed as e:
            logger_consumer.debug('Message (dt:{}) not consume'.format(method_frame.delivery_tag))
            channel.basic_reject(delivery_tag=method_frame.delivery_tag, requeue=True)
            return
        except Exception as e:
            logger_consumer.exception('Message (dt:{}) consume raise error'.format(method_frame.delivery_tag))
            channel.basic_reject(delivery_tag=method_frame.delivery_tag, requeue=True)
            if self._ignore_callback_error:
                return
            raise
        channel.basic_ack(delivery_tag=method_frame.delivery_tag)

    def declair(self, channel):
        self._declare_queue(channel)
        self._declare_exchanges(channel)
        self._declare_binds(channel)

    def run(self):
        try:
                logger_consumer.debug("Connect to rabbit")
                with pika.BlockingConnection(parameters=self._broker_connection_parameters) as connection:
                    logger_consumer.debug("Open channel")
                    with connection.channel() as channel:
                        # channel.basic_qos(prefetch_count=15)
                        self.declair(channel)

                        channel.basic_consume(self._queue, self.on_message)
                        try:
                            logger_consumer.debug("Starting consuming")
                            channel.start_consuming()
                        except KeyboardInterrupt:
                            logger_consumer.info("Consuming interrupted")
                            channel.stop_consuming()
        except Exception:
            logger_consumer.exception("Error happened in consumer")


class BlockedReconnectingConsumer(BlockedConsumer):

    def __init__(self,
                 **kwargs):
        super().__init__(**kwargs)
        self.max_reconnect_attempts = 3
        self.max_total_reconnect_attempts = self.max_reconnect_attempts * 5
        self.total_reconnect_attempts = 0
        self.is_declared = False

    def on_message(self, *args, **kwargs):
        self.total_reconnect_attempts = 0
        super().on_message(*args, **kwargs)

    def declair(self, channel):
        if not self.is_declared:
            super().declair(channel)
            self.is_declared = True

    def reconnect_pause_random_gen(self):
        yield random.randint(3, 8)

    def run(self):
        self.total_reconnect_attempts = 0
        reconnect_attempts = self.max_reconnect_attempts

        while True:
            try:
                    logger_consumer.info("Connect to rabbit")
                    with pika.BlockingConnection(parameters=self._broker_connection_parameters) as connection:
                        logger_consumer.info("Open channel")
                        with connection.channel() as channel:
                            reconnect_attempts = 0
                            # channel.basic_qos(prefetch_count=15)
                            self.declair(channel)

                            channel.basic_consume(self._queue, self.on_message)
                            try:
                                logger_consumer.info("Starting consuming")
                                channel.start_consuming()
                            except KeyboardInterrupt:
                                logger_consumer.info("Consuming interrupted")
                                channel.stop_consuming()
                                break
            except AMQPConnectionError as err:
                logger_consumer.error("Connection error on %s attempt: %s", reconnect_attempts, err)
                self.total_reconnect_attempts = self.total_reconnect_attempts + 1
                reconnect_attempts = reconnect_attempts + 1
                allow_reconnect = reconnect_attempts <= self.max_reconnect_attempts and self.total_reconnect_attempts <= self.max_total_reconnect_attempts
                if allow_reconnect:
                    pause = next(self.reconnect_pause_random_gen())
                    logger_consumer.info('Await {} before reconnect attempt'.format(pause))
                    time.sleep(pause)
                else:
                    logger_consumer.exception("Can not connect to broker")
                    break
            except Exception as err:
                logger_consumer.exception("Error happened in consumer")
                break


class BlockedPublisher(BlockedMixin):

    def __init__(self,
                 app_id=None,
                 broker_connection_parameters=None,
                 exchanges=None,
                 **kwargs):
        self._broker_connection_parameters = broker_connection_parameters
        self._exchanges = exchanges
        self._connection = None
        self._channel = None
        self._app_id = app_id or 'anonymous'

    def _publish(self,
                 exchange,
                 routing_key,
                 body,
                 correlation_id=None,
                 **kwargs):

        if not self._connection:
            logger_publisher.debug("Connect to rabbit")
            self._connection = pika.BlockingConnection(parameters=self._broker_connection_parameters)
        if not self._channel:
            logger_publisher.debug("Open channel")
            self._channel = self._connection.channel()
            self._channel.confirm_delivery()

        self._declare_exchanges(self._channel)

        return self._channel.basic_publish(
            exchange,
            routing_key,
            body,
            properties=pika.BasicProperties(
                content_type='text/json',
                delivery_mode=pika.DeliveryMode.Persistent,
                app_id=self._app_id,
                correlation_id=correlation_id,
            ),
        )

    def publish(self, *args, **kwargs):
        try:
            self._publish(*args, **kwargs)
        except pika.exceptions.ConnectionClosedByBroker as err:
            # Uncomment this to make the example not attempt recovery
            # from server-initiated connection closure, including
            # when the node is stopped cleanly
            #
            # break
            logger_publisher.debug("Caught a connection error: {}, retrying...".format(err))
            self._retry_publish(*args, **kwargs)
        # Do not recover on channel errors
        except pika.exceptions.AMQPChannelError as err:
            logger_publisher.exception("Caught a channel error: {}, stopping...".format(err))
            raise err
        # Recover on all other connection errors
        except pika.exceptions.AMQPConnectionError:
            logger_publisher.exception("Connection was closed, retrying...")
            self._retry_publish(*args, **kwargs)
        except Exception as err:
            logger_publisher.exception("Caught a error: {}, stopping...".format(err))
            raise err

    def _retry_publish(self, *args, **kwargs):
        logger_publisher.info("Retrying publish...")
        self._channel = None
        self._connection = None
        self._publish(*args, **kwargs)


class OneMessagePublisher(BlockedPublisher):

    def publish(self, exchange, *args, **kwargs):
        self._exchanges = [Exchange(exchange, ExchangeType.topic)]

        self._publish(exchange, *args, **kwargs)

        if self._channel and self._channel.is_open:
            self._channel.close()
        if self._connection and self._connection.is_open:
            self._connection.close()



def build_publisher_by_settings(publisher_class):
    return publisher_class(
        app_id=communication_settings.APP_ID,
        broker_connection_parameters=communication_settings.BROKER_CONNECTION_PARAMETERS,
        exchanges=communication_settings.EXCHANGES,
    )
