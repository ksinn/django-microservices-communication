import json
import logging
from djangorestframework_camel_case.settings import api_settings as camel_case_api_settings
from djangorestframework_camel_case import util

logger = logging.getLogger(__name__)


def underscoreize(data):
    if not data:
        return data
    return util.underscoreize(data, **camel_case_api_settings.JSON_UNDERSCOREIZE)


def camelize(data):
    if not data:
        return data
    return util.camelize(data, **camel_case_api_settings.JSON_UNDERSCOREIZE)


class MessageRouter:

    def __init__(self):
        self._handlers = {}

    def add_consumer(self, func, exchange_name, routing_key=''):
        if exchange_name not in self._handlers:
            self._handlers[exchange_name] = {}
        self._handlers[exchange_name][routing_key] = func

    def consumer(self, exchange_name, routing_key=''):
        def decorator(fun):
            self.add_consumer(fun, exchange_name, routing_key=routing_key)
            return fun
        return decorator

    def __call__(self, basic_deliver, properties, body):
        routing_key = basic_deliver.routing_key

        handler = self._get_handler(basic_deliver, properties)
        if handler:
            handler(routing_key, underscoreize(json.loads(body)))

    def _get_handler(self, basic_deliver, properties):
        routing_key = basic_deliver.routing_key
        exchange = basic_deliver.exchange

        if exchange not in self._handlers:
            logger.warning('No router for message from exchange %s with routing key %s' % (exchange, routing_key))
            return None

        exchange_handlers = self._handlers[exchange]

        handler = exchange_handlers.get(routing_key)
        if not handler:
            handler = exchange_handlers.get('')
            if not handler:
                logger.warning(
                    'No router for message from exchange %s with routing key %s' % (exchange, routing_key))
                return None
        return handler




