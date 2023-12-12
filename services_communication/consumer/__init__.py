import pytz
from datetime import datetime
from functools import wraps

from django.utils.timezone import now

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


def command_consumer(f):
    @wraps(f)
    def wrapper(routing_key, message_body, *args, **kwargs):
        meta = message_body.pop('meta', {})

        expired_time_str = meta.get('expired_time')
        if expired_time_str:
            expired_time = pytz.utc.localize(datetime.strptime(expired_time_str, '%Y-%m-%dT%H:%M:%S.%fZ'))
            if expired_time < now():
                return

        return f(routing_key, message_body, *args, **kwargs)

    return wrapper
