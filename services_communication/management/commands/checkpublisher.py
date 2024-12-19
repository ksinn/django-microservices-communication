from django.core.management import BaseCommand, CommandError
from services_communication.process import is_publisher_work

import logging

logging.basicConfig(level=logging.WARNING)


class Command(BaseCommand):
    help = "Run publisher for queued aggregate event"

    def add_arguments(self, parser):
        parser.add_argument(
            "--max_queue_size",
            type=int,
            default=0,
            help="The maximum number of unhandled events at which a publisher is considered healthy",
        )
        parser.add_argument(
            "--max_delay",
            type=int,
            default=10,
            help="The number of seconds must pass after the event to begin to consider it unprocessed",
        )

    def handle(self, *args, **options):
        is_healthy = is_publisher_work(
            max_queue_size=options['max_queue_size'],
            max_delay=options['max_delay'],
        )

        if not is_healthy:
            raise CommandError('Publisher unhealthy')

        self.stdout.write(self.style.SUCCESS('Publisher healthy'))
