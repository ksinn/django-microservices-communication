from functools import wraps
from services_communication.utils import MessageRouter

message_router = MessageRouter()


def event_consumer(f):
    @wraps(f)
    def wrapper(routing_key, message_body, *args, **kwargs):
        event_id = message_body.get('event_id')
        event_time = message_body.get('event_time')
        event_aggregate = message_body.get('aggregate')
        event_event_type = message_body.get('event_type')
        payload = message_body.get('payload')
        return f(payload,
                 event_id=event_id,
                 event_time=event_time,
                 aggregate=event_aggregate,
                 event_type=event_event_type)

    return wrapper
