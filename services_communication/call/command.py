import json

from services_communication.publisher.utils import build_publisher_by_settings
from services_communication.utils import camelize


def send_command(service_name, arguments, command_name=''):
    build_publisher_by_settings()._publish(
        exchange=service_name,
        routing_key=command_name,
        body=json.dumps(camelize(arguments))
    )
