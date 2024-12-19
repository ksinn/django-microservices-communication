from django.core.management import BaseCommand
from django.utils import autoreload

from services_communication.process import run_publisher

import logging
logging.basicConfig(level=logging.WARNING)


class Command(BaseCommand):
    help = "Run development publisher for queued aggregate event"

    def handle(self, *args, **options):
            self.stdout.write(
                self.style.SUCCESS('Starting DEVELOPMENT publisher')
            )

            try:
                autoreload.run_with_reloader(run_publisher)
            except KeyboardInterrupt:
                self.stdout.write(self.style.SUCCESS('Publisher stopped'))


