import pika

from services_communication.broker import BlockedPublisher
from services_communication.models import PublishedEventQueue
from services_communication.settings import communication_settings


def run_publisher():
    _check_publisher_settings()
    publisher = _get_publisher()
    while True:
        for event in PublishedEventQueue.objects.all():
            publisher.publish(
                exchange=event.exchange,
                routing_key=event.routing_key,
                body={
                    'eventId': event.id,
                    'eventTime': event.event_time.isoformat(),
                    'eventType': event.event_type,
                    'aggregate': event.aggregate,
                    'payload': event.payload,

                },
                properties=pika.BasicProperties(content_type='text/json',
                                                delivery_mode=pika.DeliveryMode.Persistent)
            )
            event.delete()


def _get_publisher():
    return BlockedPublisher(
        broker_url=communication_settings.BROKER_CONNECTION_URL,
        exchanges=communication_settings.EXCHANGES,
    )


def _check_publisher_settings():
    pass
