from django.utils.timezone import now

from services_communication.utils import camelize
from services_communication import publishing_backend
from services_communication.settings import communication_settings



def _add_event_in_queue(aggregate, event_type, event_time, payload, tags):
    exchange = aggregate
    routing_key = event_type

    entity_id = publishing_backend.get_id()

    body = {
        'eventId': entity_id,
        'event_time': event_time,
        'aggregate': aggregate,
        'event_type': event_type,
        'payload': camelize(payload),
    }

    publishing_backend.save_message(
        id=entity_id,
        send_after_time=event_time,
        exchange=exchange,
        routing_key=routing_key,
        body=body,
        tags=tags,
    )


def publish_aggregate_event(aggregate, event_type, payload):
    _add_event_in_queue(
        aggregate, event_type, now(),
        payload,
        None,
    )


def publish_future_aggregate_event(aggregate, event_type, event_time, payload, tags=None):
    assert communication_settings.PUBLISHER_FUTURE_EVENT_ENABLE, 'Publishing of future event not enabled in settings! Set PUBLISHER_FUTURE_EVENT_ENABLE to True'

    _add_event_in_queue(
        aggregate, event_type, event_time,
        payload,
        normalize_tags(tags),
    )


def cancel_future_aggregate_event(aggregate, event_type, tags):
    assert tags, "Tags cant not be empty for canceling future event"

    norm_tags = normalize_tags(tags)

    publishing_backend.delete_by_tags_subset(aggregate, event_type, norm_tags)

def normalize_tags(tags):
    if not tags:
        return None

    return {k: str(v) for k, v in tags.items()}

