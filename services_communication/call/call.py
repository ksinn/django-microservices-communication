from datetime import timedelta

from django.utils.timezone import now

from services_communication.utils import camelize
from services_communication import publishing_backend



def send_call(service_name, method_name, data, reply_to=None, timeout=None, expired_time=None):

    assert reply_to, "Exchange for reply not set!"
    assert not (timeout and expired_time), "Ambiguous timeout! Use timeout or expired_time, not both"
    assert expired_time is None or expired_time > now(), "expired_time in past!"

    meta = {
        'reply_to': reply_to,
        'time': now(),
    }

    if timeout:
        expired_time = now() + timedelta(seconds=timeout)

    if expired_time:
        meta['expired_time'] = expired_time

    call_id = publishing_backend.get_id()

    body = {
        'id': call_id,
        'meta': meta,
        'data': data,
    }

    publishing_backend.save_message(
        id=call_id,
        send_after_time=now(),
        exchange=service_name,
        routing_key=method_name,
        body=camelize(body),
        tags=None,
    )

    return call_id