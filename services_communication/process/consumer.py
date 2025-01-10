from services_communication.settings import communication_settings


def run_consumer():
    _check_consumer_settings()
    consumer = _get_consumer()
    consumer.run()


def _get_consumer():
    return communication_settings.CONSUMER_CLASS(
        broker_connection_parameters=communication_settings.BROKER_CONNECTION_PARAMETERS,
        queue=communication_settings.QUEUE,
        exchanges=communication_settings.EXCHANGES,
        binds=communication_settings.BINDS,
        on_message_callback=communication_settings.MESSAGE_CONSUMER,
    )


def _check_consumer_settings():
    assert communication_settings.BROKER_CONNECTION_PARAMETERS, 'Broker connection not set!'
    assert communication_settings.QUEUE, 'Broker queue for consuming not set!'
