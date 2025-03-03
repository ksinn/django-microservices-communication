import json
from datetime import timedelta

from django.core.serializers.json import DjangoJSONEncoder
from django.utils.timezone import now

from services_communication.process.publisher import build_publisher_by_settings
from services_communication.utils import camelize


def send_command(service_name, arguments, command_name='', timeout=None, expired_time=None):
    assert not (timeout and expired_time), "Ambiguous timeout! Use timeout or expired_time, not both"
    assert expired_time is None or expired_time > now(), "expired_time in past!"

    meta = {}

    if timeout:
        expired_time = now() + timedelta(seconds=timeout)

    if expired_time:
        meta['expired_time'] = expired_time

    arguments['meta'] = meta

    build_publisher_by_settings()._publish(
        exchange=service_name,
        routing_key=command_name,
        body=json.dumps(camelize(arguments), cls=DjangoJSONEncoder)
    )
