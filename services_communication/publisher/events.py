from django.utils.timezone import now

from services_communication.models import PublishedEventQueue
from services_communication.utils import camelize
from .utils import is_future_event_enabled


def add_event_in_queue(aggregate, event_type, event_time, payload, tags):
    exchange = aggregate
    routing_key = event_type

    PublishedEventQueue.objects.create(
        exchange=exchange,
        routing_key=routing_key,

        event_time=event_time,
        aggregate=aggregate,
        event_type=event_type,
        payload=camelize(payload),
        tags=tags,
    )


def publish_aggregate_event(aggregate, event_type, payload):
    add_event_in_queue(
        aggregate, event_type, now(),
        payload,
        None,
    )


def publish_future_aggregate_event(aggregate, event_type, event_time, payload, tags=None):
    assert is_future_event_enabled(), "Publishing of future event not enabled in settings! Set PUBLISHER_FUTURE_EVENT_ENABLE to True"
    add_event_in_queue(
        aggregate, event_type, event_time,
        payload,
        normalize_tags(tags),
    )


def cancel_future_aggregate_event(aggregate, event_type, tags):
    assert is_future_event_enabled(), "Publishing of future event not enabled in settings! Set PUBLISHER_FUTURE_EVENT_ENABLE to True"
    assert tags, "Tags cant not be empty for canceling future event"

    norm_tags = normalize_tags(tags)

    PublishedEventQueue.objects.filter(tags__contains=norm_tags).delete()


def get_events_for_send_to_broker():
    qs = PublishedEventQueue.objects.all()
    if is_future_event_enabled():
        qs = qs.filter(event_time__lte=now())
    return qs


def normalize_tags(tags):
    if not tags:
        return None

    return {k: str(v) for k, v in tags.items()}
