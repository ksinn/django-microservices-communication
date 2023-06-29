from services_communication.settings import communication_settings


def build_publisher_by_settings():
    return communication_settings.CONSUMER_CLASS(
        app_id=communication_settings.APP_ID,
        broker_url=communication_settings.BROKER_CONNECTION_URL,
        exchanges=communication_settings.EXCHANGES,
    )


def check_publisher_settings():
    pass
