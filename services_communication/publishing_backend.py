from django.db import connections
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


def get_db_alias():
    return PublishedEventQueue.objects.db


def get_scheme_and_tabel_name():
    table = PublishedEventQueue._meta.db_table

    connection = connections[get_db_alias()]
    with connection.cursor() as cursor:
        cursor.execute(
            """SHOW search_path;""",
        )

        search_path = cursor.fetchone()[0]
        if not search_path:
            raise Exception('Database search_path is empty!')

        search_path_schemes = search_path.split(',')

    with connection.cursor() as cursor:
        cursor.execute(
            """SELECT table_schema FROM information_schema.tables WHERE table_name = %s AND table_schema = ANY(%s);""",
            (table, search_path_schemes),
        )

        schemes_has_tabel = set(row[0] for row in cursor.fetchall())

    schema = None
    for available_scheme in search_path_schemes:
        if available_scheme in schemes_has_tabel:
            schema = available_scheme
            break

    if not schema:
        raise Exception('Not found db schema used for tabel {}!'.format(table))

    return schema, table