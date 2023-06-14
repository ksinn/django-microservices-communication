from django.db import models

class TestM(models.Model):
    a = models.CharField(max_length=1)