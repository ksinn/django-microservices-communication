import pytz
from datetime import datetime
from functools import wraps

from django.db.transaction import atomic
from django.utils.timezone import now

from services_communication.utils import camelize
from services_communication import publishing_backend
from services_communication.defaults import message_router as _message_router
message_router = _message_router


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


def call_consumer(f):
    @atomic
    @wraps(f)
    def wrapper(routing_key, message_body, *args, exchange=None, **kwargs):
        call_id = message_body['id']
        request_meta = message_body.pop('meta', {})
        request_data = message_body.pop('data', {})


        expired_time_str = request_meta.get('expired_time')
        if expired_time_str:
            expired_time = pytz.utc.localize(datetime.strptime(expired_time_str, '%Y-%m-%dT%H:%M:%S.%fZ'))
            if expired_time < now():
                return


        response = f(request_data, *args, method_name=routing_key, call_id=call_id, meta=request_meta, **kwargs)
        # Если тут поймать ошибку и не прокинуть ее выше, то не произойдет откат транзакции, а это не допустимо.
        # Кроме того, как в это случае "возвращать" ответ, ведь ответ то тоже требует записи в базу.

        reply_to = request_meta['reply_to']
        response_meta = {
            'time': now(),
        }

        body = {
            'id': call_id,
            'data': response,
            'meta': response_meta,
        }

        publishing_backend.save_message(
            id=publishing_backend.get_id(),
            send_after_time=now(),
            exchange=reply_to,
            routing_key=f'call-response.{exchange}.{routing_key}',
            body=camelize(body),
            tags=None,
        )
        return

    return wrapper


def call_response_consumer(f):
    @wraps(f)
    def wrapper(routing_key, message_body, *args, exchange=None, **kwargs):
        call_id = message_body['id']
        request_meta = message_body.pop('meta', {})
        request_data = message_body.pop('data', {})

        _, service_name, method_name = routing_key.split('.', 2)

        response = f(request_data, *args, service_name=service_name, method_name=method_name, call_id=call_id, meta=request_meta, **kwargs)
    return wrapper
