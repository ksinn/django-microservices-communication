from django.db.models import Q
from django.utils.timezone import now

from services_communication.models import PublishedEventQueue


def get_messages_for_send_to_broker():
    qs = PublishedEventQueue.objects.filter(Q(send_after_time__lte=now()) | Q(event_time__lte=now()))
    return qs

def get_id():
    return PublishedEventQueue.get_next_id_value()

def save_message(id, exchange, routing_key, send_after_time, body, tags):
    PublishedEventQueue.objects.create(
        id=id,
        send_after_time=send_after_time,
        exchange=exchange,
        routing_key=routing_key,
        body=body,
        is_new_style=True,
        tags=tags,
    )


def delete(message):
    message.delete()


def delete_by_tags_subset(exchange, routing_key, tags):
    PublishedEventQueue.objects.filter(exchange=exchange, routing_key=routing_key, tags__contains=tags).delete()