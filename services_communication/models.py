from django.db import models
from django.core.serializers.json import DjangoJSONEncoder


class PublishedEventQueue(models.Model):
    exchange = models.CharField(max_length=64)
    routing_key = models.CharField(max_length=256)

    event_time = models.DateTimeField(auto_now_add=True)
    aggregate = models.CharField(max_length=64)
    event_type = models.CharField(max_length=64)
    payload = models.JSONField(encoder=DjangoJSONEncoder)

