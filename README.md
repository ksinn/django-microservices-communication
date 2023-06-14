Pub/Sub for service on django
=======================

Installation
-----------------
```commandline
 pip install git+https://github.com/ksinn/django-microservices-communication
```

Consuming
----------------

Add 'services_communication' to your INSTALLED_APPS setting.
```python
INSTALLED_APPS = [
    ...
    'services_communication',
]
```

Any global settings are kept in a single configuration dictionary named MICROSERVICES_COMMUNICATION_SETTINGS. Start off by adding the following to your settings.py module:
```python
MICROSERVICES_COMMUNICATION_SETTINGS = {
    'BROKER_CONNECTION_URL': 'amqp://guest:guest@localhost:5672',
    'QUEUE': 'my_queue',
    'EXCHANGES': [
        'my_exchange1',
        ('my_exchange1', 'topic'),
    ],
    'BINDS': [
        ('my_exchange1', 'event.*'),
        'my_exchange2',
    ],
}
```

Write logical consuming function in file 'consumers.py' in django app
```
some_project/
    | some_project/
        | settings.py
        | urls.py
    | some_app/
        | __init__.py
        | admin.py
        | apps.py
        | consumers.py  <---- 
        | models.py
        | tests.py
        | viwes.py
    | some_other_app/
        | __init__.py
        | admin.py
        | apps.py
        | consumers.py  <----
        | models.py
        | tests.py
        | viwes.py
```

Every consumer function must be registered in message router.

Example  consumers.py file:
```
from services_communication.consumer import message_router

@message_router.consumer('my_exchange1', 'event.update')
@message_router.consumer('my_exchange1', 'event.create')
@message_router.consumer('my_exchange2')  // For get all routing keys
def stupid_consume_function(routing_key, body):
    print(routing_key, body)
```

Run consumer
```commandline
python manage.py runconsumer
```