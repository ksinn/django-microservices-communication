import json
import time
import pika

from services_communication.models import PublishedEventQueue
from services_communication.publisher.utils import build_publisher_by_settings


def run_publisher():
    _check_publisher_settings()
    publisher = _get_publisher()
    while True:
        for event in PublishedEventQueue.objects.all():
            publisher.publish(
                exchange=event.exchange,
                routing_key=event.routing_key,
                body=json.dumps({
                    'eventId': event.id,
                    'eventTime': event.event_time.isoformat(),
                    'eventType': event.event_type,
                    'aggregate': event.aggregate,
                    'payload': event.payload,

                }),
            )
            event.delete()
        time.sleep(1)


def _get_publisher():
    return build_publisher_by_settings()


def _check_publisher_settings():
    pass
