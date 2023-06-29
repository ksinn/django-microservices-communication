import json
import time

from services_communication.models import PublishedEventQueue
from services_communication.publisher import utils


def run_publisher():
    utils.check_publisher_settings()
    publisher = utils.build_publisher_by_settings()
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

