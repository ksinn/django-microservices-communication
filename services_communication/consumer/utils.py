from services_communication.settings import communication_settings
from services_communication.logging import get_logger

logger = get_logger(__name__)


def build_consumer_by_settings():
    return communication_settings.CONSUMER_CLASS(
        broker_url=communication_settings.BROKER_CONNECTION_URL,
        queue=communication_settings.QUEUE,
        exchanges=communication_settings.EXCHANGES,
        binds=communication_settings.BINDS,
        on_message_callback=communication_settings.MESSAGE_CONSUMER,
    )


def check_consumer_settings():
    pass
