from collections import namedtuple

Exchange = namedtuple("Exchange", ['name', 'type'])
Bind = namedtuple("Bind", ['exchange', 'routing_key'])