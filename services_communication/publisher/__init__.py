from services_communication.models import PublishedEventQueue
from services_communication.utils import camelize


def publish_aggregate_event(aggregate, event_type, payload):
    exchange = aggregate
    routing_key = event_type

    PublishedEventQueue.objects.create(
        exchange=exchange,
        routing_key=routing_key,

        aggregate=aggregate,
        event_type=event_type,
        payload=camelize(payload),
    )
