import os
from collections import namedtuple
from typing import Tuple

from django.conf import settings
from django.utils.module_loading import import_string
from pika.exchange_type import ExchangeType

DEFAULT = {
    'LOG_LEVEL': 'ERROR',
    'APP_ID': None,  # Use for publisher
    'BROKER_CONNECTION_URL': 'amqp://guest:guest@localhost:5672',  # The AMQP url to connect with'
    'QUEUE': '',  # The AMQP queue for consume'
    'EXCHANGES': [
    ],  # The AMQP exchanges for publisher or consumer binds. String or tuple of name and type

    'BINDS': [
    ],  # The AMQP binds for consumer. String or tuple of exchange name and routing keys'
    'CONSUMER_CLASS': 'services_communication.broker.BlockedConsumer',
    'MESSAGE_CONSUMER': 'services_communication.consumer.message_router',
    # 'MESSAGE_CONSUMER_IGNORE_ERRORS': (
    #     django.db.utils.InterfaceError,
    # ),

    'REST_API_HOST': 'http://localhost:8000',
    'REST_API_USERNAME': 'username',
    'REST_API_PASSWORD': 'password',
    'REST_API_AUTH_URL': 'api/v1/auth',
    # Callback func(basic_deliver, properties, body)
}

Exchange = namedtuple("Exchange", ['name', 'type'])
Bind = namedtuple("Bind", ['exchange', 'routing_key'])


class Settings:
    LOG_LEVEL = None
    APP_ID = None
    BROKER_CONNECTION_URL: str = None
    QUEUE: str = None
    EXCHANGES: Tuple[Exchange] = None
    BINDS: Tuple[Bind] = None
    MESSAGE_CONSUMER = None
    CONSUMER_CLASS = None
    # CONSUMER_IGNORE_ERRORS = None
    REST_API_HOST = None
    REST_API_USERNAME = None
    REST_API_PASSWORD = None
    REST_API_AUTH_URL = None

    def __init__(self, default, user):
        if not user:
            user = {}

        self.BROKER_CONNECTION_URL = self.get_value("BROKER_CONNECTION_URL", default, user)
        self.QUEUE = self.get_value("QUEUE", default, user)
        self.MESSAGE_CONSUMER = import_string(self.get_value("MESSAGE_CONSUMER", default, user))
        # self.MESSAGE_CONSUMER_IGNORE_ERRORS = user.get("MESSAGE_CONSUMER_IGNORE_ERRORS") or default["MESSAGE_CONSUMER_IGNORE_ERRORS"]
        self.CONSUMER_CLASS = import_string(self.get_value("CONSUMER_CLASS", default, user))

        self.APP_ID = self.get_value("APP_ID", default, user) or self.get_django_project_name()

        exchanges = self.get_value("EXCHANGES", default, user)
        self.EXCHANGES = tuple(map(self.build_exchange, exchanges))

        binds = self.get_value("BINDS", default, user)
        self.BINDS = tuple(map(self.build_bind, binds))

        self.QUEUE = self.get_value("QUEUE", default, user)

        self.REST_API_HOST = self.get_value("REST_API_HOST", default, user)
        self.REST_API_USERNAME = self.get_value("REST_API_USERNAME", default, user)
        self.REST_API_PASSWORD = self.get_value("REST_API_PASSWORD", default, user)
        self.REST_API_AUTH_URL = self.get_value("REST_API_AUTH_URL", default, user)


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
        return default[key]

    def get_django_project_name(self):
        return os.environ['DJANGO_SETTINGS_MODULE'].split('.')[0]



communication_settings = Settings(DEFAULT, getattr(settings, 'MICROSERVICES_COMMUNICATION_SETTINGS', None))
