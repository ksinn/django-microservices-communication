import logging
from datetime import timedelta

from django.utils.timezone import now

from services_communication import publishing_backend
from services_communication.settings import communication_settings


logger = logging.getLogger('services_communication.publisher.process')


def run_publisher():
    _check_publisher_settings()
    publisher = _get_publisher()
    publisher.run()


def is_publisher_work(max_queue_size=0, max_delay=15):
    created_before_time = now() - timedelta(seconds=max_delay)
    queue_size = publishing_backend.get_messages_for_send_to_broker().filter(event_time__lt=created_before_time).count()

    return queue_size <= max_queue_size


def _get_publisher():
    return build_publisher_by_settings()


def _check_publisher_settings():
    assert communication_settings.BROKER_CONNECTION_PARAMETERS, 'Broker connection not set!'

def build_publisher_by_settings():
    return communication_settings.MESSAGE_PUBLISHER_QUEUE_HANDLER_CLASS(
        app_id=communication_settings.APP_ID,
        broker_connection_parameters=communication_settings.BROKER_CONNECTION_PARAMETERS,
        exchanges=communication_settings.EXCHANGES,
    )
