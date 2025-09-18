import logging

from django.core.management import BaseCommand
from services_communication.process import run_consumer

from django.utils import autoreload

logger = logging.getLogger('services_communication.consumer')

class Command(BaseCommand):
    help = "Run dev consumer"

    def handle(self, *args, **options):
            self.stdout.write(
                self.style.SUCCESS('Starting DEVELOPMENT consumer')
            )

            try:
                autoreload.run_with_reloader(run_consumer)
            except KeyboardInterrupt:
                self.stdout.write(self.style.SUCCESS('Consumer stopped'))


