from django.db import models, connection
from django.core.serializers.json import DjangoJSONEncoder


class PublishedEventQueue(models.Model):
    id = models.IntegerField(primary_key=True)
    create_time = models.DateTimeField(auto_now_add=True)

    is_new_style = models.BooleanField(null=True)

    exchange = models.CharField(max_length=64)
    routing_key = models.CharField(max_length=256)
    body = models.JSONField(null=True, encoder=DjangoJSONEncoder)

    event_time = models.DateTimeField(null=True)
    aggregate = models.CharField(null=True, max_length=64)
    event_type = models.CharField(null=True, max_length=64)
    payload = models.JSONField(null=True, encoder=DjangoJSONEncoder)

    send_after_time = models.DateTimeField(null=True)
    tags = models.JSONField(null=True)

    @classmethod
    def get_next_id_value(cls):
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT nextval('services_communication_publishedeventqueue_id_seq');")
            result = cursor.fetchone()
        return result[0]