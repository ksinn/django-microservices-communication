Easy communication for django based microservices
=======================
Library provides tools for:
- Publisher/Subscription pattern
- Sending async command
- REST API 

Installation
----------------
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
    'APP_ID': 'my-service',
    'BROKER_CONNECTION_URL': 'amqp://guest:guest@localhost:5672',
    # or set as connection params dict
    'BROKER_CONNECTION_PARAMETERS': {
        'host': 'localhost',
        'port': 5672,
        'virtual_host': None,
        'username': 'guest',
        'password': 'guest',
        # Instead username and password you may set pika credentials object
        'credentials': pika.PlainCredentials('guest', 'guest')
    },
    'QUEUE': 'my-queue',
    'EXCHANGES': [
        'my-exchange1',
        ('my-other-exchange', 'fanout'),
        'exchange3',
    ],
    'BINDS': [
        ('my-exchange1', 'event.*'),
        'my-other-exchange',
    ],
    
    'REST_API_HOST': 'http://api.example.com', 
    'REST_API_AUTH_URL': 'api/v1/login',
    
    # Set auth request body
    'REST_API_CREDENTIAL': {
        'login': 'sarvar',
        'password': 'sarvar',
    },
    
    # Or username and password, if filed named as 'username' and 'password'
    'REST_API_USERNAME': 'myusername',
    'REST_API_PASSWORD': '12345',
    
    # Set True for use future event
    'PUBLISHER_FUTURE_EVENT_ENABLE': False,
}
```
Defaults:
- exchange type - _topic_
- bind routing key - _'#'_


*Async communication*
---------------------------------

Consuming
----------------

Run consumer
```commandline
python manage.py runconsumer
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

Consumer function must be registered in message router.
Basic consumer function mast accept 2 positional arguments: _routing key_ and _message body_.

Example  consumers.py file:
```
from services_communication.consumer import message_router

@message_router.consumer('my-exchange1', 'event.update')
@message_router.consumer('my-exchange1', 'event.create')
@message_router.consumer('my-other-exchange')  # For get all routing keys
@message_router.consumer()  # For get all exchange (default consumer)
def stupid_consume_function(routing_key, body):
    print(routing_key, body)


@message_router.default_consumer  # For get message not routed to other consumers
def stupid_consume_function(routing_key, body):
    print(payload)
```

If you want to consume aggregate event, use decorator _@event_consumer_ and after then consumer function mast accept only on positional argument _event payload_ and other event data as _kwargs_
Example  consumers.py file:
```
from services_communication.consumer import message_router

@message_router.consumer('my-exchange1', 'event.update')
@message_router.consumer('my-exchange1', 'event.create')
@message_router.consumer('my-ether_exchange')  # For get all routing keys
@event_consumer
def stupid_consume_function(payload, **kwargs):
    print(payload)
```


Or user _devconsumer_ for auto reloading on change files

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

*Scheduling future event (in transaction)*

Work the same as regular events, but you can specify a time (in the future) when the event will be sent. 
Tags can be used to later cancel an event. Tag values are cast to string and value 1 equals '1', but not equals True!
Need _PUBLISHER_FUTURE_EVENT_ENABLE_ setting in True.

```python
from services_communication.publisher import publish_future_aggregate_event, cancel_future_aggregate_event


def registrate_user(user):
    ....
    user.save()
    
    # remind the user to set a photo
    publish_future_aggregate_event(
        aggregate='user',
        event_type='remind.photo',
        event_time=now() + timedelta(seconds=delay),
        payload=build_user_data(user),
        tags={'user_id': user.id, 'any_other_tag': 'any_value'}
        
    )

def set_user_photo(user, photo):
    user.photo = photo
    user.save()
    
    # cancel remind
    cancel_future_aggregate_event(
        aggregate='user',
        event_type='remind.photo',
        tags={'user_id': user.id}
        
    )
```

Run publisher process
```commandline
python manage.py runpublisher
```

Or user _devpublisher_ for auto reloading on change files

Commands
--------------
A command is a way of telling remote service to do something without waiting for a response from it.

For send command immediately, without regard to transactionality, use _send_command_ with service name and payloads as arguments.

You can set timeout in seconds for command executing, this means that the executor of the command should not execute it if the specified time has passed since the time it was sent (called _send_command_ function).

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


*Sync communication*
---------------------

REST API
----------
For request endpoint use method functions from rest_api package.

```python
from services_communication.rest_api import get, post, head, delete
from services_communication.rest_api.formatter import full_response

first_subject = get('api/v1/subjects/1')  # return only response body as dict

first_subject = get(
    'api/v1/subjects',
    params={
        'page': 2,
        'size': 20,
    },
)  # sending query params

response = get('api/v1/subjects/1', response_formatter=full_response)  # return response object

new_subject = post(
    'api/v1/subjects',
    json={
        'name': 'My new subject',
        'order': 5,
    },
)  # sending request body
```
In all methods function you can send additional keyword argument, it was sent to request.

For formatting request and response uoy can send custom function as *request_formatter* and *response_formatter* keyword arguments. 

*request_formatter* will be applied to other request arguments(params, json, data).

*response_formatter* will be applied to response and it result be returned from method.

By default:

- get, post, delete methods return response.json
- head method return full response


Versions
-------------
* 2.4.x

2.4.1 - Fix: add pytz requirements

2.4.0 - Add future events

* 2.3.x

2.3.8 - Fix: add pytz requirements

2.3.6 - Add extra host param for rest api

2.3.5 - Fix loading module with consumers

2.3.4 - Fix logging configration

2.3.3 - Fix consumer: down on db connection error

2.3.1 - Allow set broker connection parameters as dict in settings


* 2.2.x

2.2.5 - Fix: add pytz requirements

2.2.4 - Fix loading module with consumers

2.2.3 - Fix consumer: down on db connection error

* 2.1.x

2.1.5 - Fix: add pytz requirements

2.1.4 - Allow set rest api auth credentials and url in settings

2.1.3 - Fix loading module with consumers

2.1.2 - Fix consumer: down on db connection error

2.1.1 - Fix api error handling

2.1.0 - Any fix in consuming
