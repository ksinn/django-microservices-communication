from django.core.management import BaseCommand
from services_communication.publisher.process import run_publisher

import logging
logging.basicConfig(level=logging.WARNING)


class Command(BaseCommand):
    help = "Run publisher for queued aggregate event"

    def handle(self, *args, **options):
            self.stdout.write(
                self.style.SUCCESS('Starting publisher')
            )

            try:
                run_publisher()
            except KeyboardInterrupt:
                self.style.SUCCESS('Publisher stopped')


