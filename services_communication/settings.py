import os
from collections import namedtuple
from typing import Tuple

import pika
from django.conf import settings
from django.utils.functional import LazyObject
from django.utils.module_loading import import_string
from pika.exchange_type import ExchangeType

DEFAULT = {
    'LOG_LEVEL': 'ERROR',
    'APP_ID': None,  # Use for publisher
    'BROKER_CONNECTION_URL': 'amqp://guest:guest@localhost:5672',  # The AMQP url to connect with'
    'BROKER_CONNECTION_PARAMETERS': None,
    # 'BROKER_CONNECTION_PARAMETERS': {
    #     'host': 'localhost',
    #     'port': 5672,
    #     'virtual_host': None,
    #     'username': 'guest',
    #     'password': 'guest',
    #     'credentials': pika.PlainCredentials('guest', 'guest')
    # },
    'QUEUE': '',  # The AMQP queue for consume'
    'EXCHANGES': [
    ],  # The AMQP exchanges for publisher or consumer binds. String or tuple of name and type

    'BINDS': [
    ],  # The AMQP binds for consumer. String or tuple of exchange name and routing keys'
    'CONSUMER_CLASS': 'services_communication.broker.BlockedConsumer',
    'MESSAGE_CONSUMER': 'services_communication.consumer.message_router',
    'MESSAGE_PUBLISHER_QUEUE_HANDLER_CLASS': 'services_communication.publisher.queue_handler.ListenPublisherQueueHandler',
    # Callback func(basic_deliver, properties, body)

    'REST_API_HOST': 'http://localhost:8000',
    'REST_API_CREDENTIAL': None,  # {"username": "username", "password": "123456"}
    'REST_API_AUTH_URL': None,  # 'api/v1/auth',
    'PUBLISHER_FUTURE_EVENT_ENABLE': False,
}

Exchange = namedtuple("Exchange", ['name', 'type'])
Bind = namedtuple("Bind", ['exchange', 'routing_key'])


class Settings:
    LOG_LEVEL = None
    APP_ID = None
    BROKER_CONNECTION_PARAMETERS: pika.connection.Parameters = None
    QUEUE: str = None
    EXCHANGES: Tuple[Exchange] = None
    BINDS: Tuple[Bind] = None
    MESSAGE_CONSUMER = None
    CONSUMER_CLASS = None
    MESSAGE_PUBLISHER_QUEUE_HANDLER_CLASS = None
    REST_API_HOST = None
    REST_API_CREDENTIAL = None
    REST_API_AUTH_URL = None
    PUBLISHER_FUTURE_EVENT_ENABLE = None

    def __init__(self, default, user):
        if not user:
            user = {}

        self.BROKER_CONNECTION_PARAMETERS = self.get_broker_connection_parameters(default, user)
        self.QUEUE = self.get_value("QUEUE", default, user)
        self.MESSAGE_CONSUMER = import_string(self.get_value("MESSAGE_CONSUMER", default, user))
        self.CONSUMER_CLASS = import_string(self.get_value("CONSUMER_CLASS", default, user))

        self.MESSAGE_PUBLISHER_QUEUE_HANDLER_CLASS = import_string(self.get_value("MESSAGE_PUBLISHER_QUEUE_HANDLER_CLASS", default, user))

        self.APP_ID = self.get_value("APP_ID", default, user) or self.get_django_project_name()

        exchanges = self.get_value("EXCHANGES", default, user)
        self.EXCHANGES = tuple(map(self.build_exchange, exchanges))

        binds = self.get_value("BINDS", default, user)
        self.BINDS = tuple(map(self.build_bind, binds))

        self.QUEUE = self.get_value("QUEUE", default, user)

        self.REST_API_HOST = self.get_value("REST_API_HOST", default, user)
        self.REST_API_AUTH_URL = self.get_value("REST_API_AUTH_URL", default, user)
        self.REST_API_CREDENTIAL = self.get_rest_api_credential(default, user)
        self.PUBLISHER_FUTURE_EVENT_ENABLE = self.get_value("PUBLISHER_FUTURE_EVENT_ENABLE", default, user)

    def build_bind(self, bind_settings):
        if isinstance(bind_settings, str):
            return Bind(exchange=bind_settings, routing_key='#')
        if (isinstance(bind_settings, list) or isinstance(bind_settings, tuple)) and len(bind_settings) == 2:
            return Bind(exchange=bind_settings[0], routing_key=bind_settings[1])
        raise Exception(
            "MICROSERVICES_COMMUNICATION_SETTINGS.BINDS "
            "element mast by str with name "
            "or tuple with 2 elements: exchange and routing key"
        )

    def build_exchange(self, exchange_settings):
        if isinstance(exchange_settings, str):
            return Exchange(name=exchange_settings, type=ExchangeType.topic)
        if (isinstance(exchange_settings, list) or isinstance(exchange_settings, tuple)) and len(
                exchange_settings) == 2:
            return Exchange(name=exchange_settings[0], type=exchange_settings[1])
        raise Exception(
            "MICROSERVICES_COMMUNICATION_SETTINGS.EXCHANGES "
            "element mast by str with name "
            "or tuple with 2 elements: name and type"
        )

    def get_value(self, key, default, user):
        if key in user:
            return user[key]


        if hasattr(settings, f'MICROSERVICES_COMMUNICATION_SETTING_{key}'):
            return getattr(settings, f'MICROSERVICES_COMMUNICATION_SETTING_{key}')

        return default[key]

    def get_django_project_name(self):
        return os.environ['DJANGO_SETTINGS_MODULE'].split('.')[0]

    def get_rest_api_credential(self, default, user):
        credential = self.get_value("REST_API_CREDENTIAL", default, user)
        if credential:
            return credential

        username = user.get("REST_API_USERNAME", None)
        password = user.get("REST_API_PASSWORD", None)

        if username or password:
            return {
                "username": username,
                "password": password,
            }

        return None

    def get_broker_connection_parameters(self, default, user):
        parameters = self.get_value("BROKER_CONNECTION_PARAMETERS", default, user)
        if not parameters:
            connection_url = self.get_value("BROKER_CONNECTION_URL", default, user)
            return pika.URLParameters(connection_url) if connection_url else None

        assert isinstance(parameters, dict), 'MICROSERVICES_COMMUNICATION_SETTINGS.BROKER_CONNECTION_PARAMETERS mast be dict, not {}'.format(
            type(parameters))

        prepared_parameters = parameters.copy()
        for key, value in parameters.items():
            if not value:
                prepared_parameters.pop(key)

        if 'credentials' not in prepared_parameters:
            username = prepared_parameters.pop('username', 'guest')
            password = prepared_parameters.pop('password', 'guest')
            prepared_parameters['credentials'] = pika.PlainCredentials(username, password)

        return pika.ConnectionParameters(**prepared_parameters)


class LazySettings(LazyObject):

    def _setup(self):
        self._wrapped = Settings(DEFAULT, getattr(settings, 'MICROSERVICES_COMMUNICATION_SETTINGS', None))

communication_settings = LazySettings()
