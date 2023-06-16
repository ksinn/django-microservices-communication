from services_communication.broker import BlockedPublisher
from services_communication.settings import communication_settings


def build_publisher_by_settings():
    return BlockedPublisher(
        broker_url=communication_settings.BROKER_CONNECTION_URL,
        exchanges=communication_settings.EXCHANGES,
    )
