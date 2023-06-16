Pub/Sub for service on django
=======================

Installation
-----------------
```commandline
 pip install git+https://github.com/ksinn/django-microservices-communication
```

In _requirements.txt_ file
```python
...
Django==4.2
git+https://github.com/ksinn/django-microservices-communication
django-cors-headers==3.14.0
...
```
*Installation in Docker*
If pip install execute in docker, you require git in image.


Add 'services_communication' to your INSTALLED_APPS setting.
```python
INSTALLED_APPS = [
    ...
    'services_communication',
]
```

Any global settings are kept in a single configuration dictionary named MICROSERVICES_COMMUNICATION_SETTINGS. 
Start off by adding the following to your settings.py module:
```python
MICROSERVICES_COMMUNICATION_SETTINGS = {
    'BROKER_CONNECTION_URL': 'amqp://guest:guest@localhost:5672',
    'QUEUE': 'my_queue',
    'EXCHANGES': [
        'my_exchange1',
        ('my_other_exchange', 'fanout'),
        'exchange3',
    ],
    'BINDS': [
        ('my_exchange1', 'event.*'),
        'my_other_exchange',
    ],
}
```
Defaults:
- exchange type - _topic_
- bind routing key - _'#'_

Consuming
----------------
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
@message_router.consumer('my_other_exchange')  # For get all routing keys
def stupid_consume_function(routing_key, body):
    print(routing_key, body)
```

Run consumer
```commandline
python manage.py runconsumer
```

Publishing
--------------

*Publishing in transaction*
For publish event happened with [aggregate](https://microservices.io/patterns/data/aggregate.html) in transaction use publish_aggregate_event
```python
from services_communication.publisher import publish_aggregate_event

def update_user_name(user, new_name):
    user.name = new_name
    user.save()
    publish_aggregate_event(
                aggregate='user',
                event_type='update.base',
                payload=build_user_data(user),
            )
```

This function save event data in db table. 
Then publisher process will read the event from the table and publish it to the broker in _exchange_ same as aggregate name with _routing key_ same as event type,
                event_type and body:
```json
{
    "eventId": "2",
    "eventTime": "2023-06-02T10:58:58.340174Z",
    "eventType": "update.base",
    "aggregate": "user",
    "payload": {
      ...
    },
}
```


Run publisher process
```commandline
python manage.py runpublisher
```

Commands
--------------
A command is a way of telling remote service to do something without waiting for a response from it.

For send command immediately, without regard to transactionality, use _send_command_ with service name and payloads as arguments.

```python
from services_communication.call import send_command

send_command(
    'sms',
    {
        'phone': '998990000000',
        'text': 'Hello world!',
    }
)
```

If remote service has any commands, you may want to use optional argument _command_name_.