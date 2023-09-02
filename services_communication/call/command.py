import json
from datetime import timedelta

from django.core.serializers.json import DjangoJSONEncoder
from django.utils.timezone import now

from services_communication.publisher.utils import build_publisher_by_settings
from services_communication.utils import camelize


def send_command(service_name, arguments, command_name='', timeout=None):
    meta = {}

    if timeout:
        meta['expired_time'] = now() + timedelta(seconds=timeout)

    arguments['meta'] = meta

    build_publisher_by_settings()._publish(
        exchange=service_name,
        routing_key=command_name,
        body=json.dumps(camelize(arguments), cls=DjangoJSONEncoder)
    )
