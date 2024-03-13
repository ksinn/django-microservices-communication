from services_communication.broker import BlockedPublisher
from services_communication.settings import communication_settings


def build_publisher_by_settings():
    assert communication_settings.BROKER_CONNECTION_PARAMETERS, 'Broker connection not set!'

    return BlockedPublisher(
        app_id=communication_settings.APP_ID,
        broker_connection_parameters=communication_settings.BROKER_CONNECTION_PARAMETERS,
        exchanges=communication_settings.EXCHANGES,
    )


def is_future_event_enabled():
    return communication_settings.PUBLISHER_FUTURE_EVENT_ENABLE is True
