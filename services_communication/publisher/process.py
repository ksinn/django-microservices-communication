import json
import time
from datetime import timedelta

import pika
from django.utils.timezone import now

from services_communication.models import PublishedEventQueue
from services_communication.publisher.events import get_events_for_send_to_broker
from services_communication.publisher.utils import build_publisher_by_settings


def run_publisher():
    _check_publisher_settings()
    publisher = _get_publisher()
    while True:
        for event in get_events_for_send_to_broker():
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


def is_publisher_work(max_queue_size=0, max_delay=15):
    created_before_time = now() - timedelta(seconds=max_delay)
    queue_size = get_events_for_send_to_broker().filter(event_time__lt=created_before_time).count()

    return queue_size <= max_queue_size


def _get_publisher():
    return build_publisher_by_settings()


def _check_publisher_settings():
    pass
