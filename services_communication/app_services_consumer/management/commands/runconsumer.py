from django.core.management import BaseCommand
from services_communication.app_services_consumer.process import run_consumer

import logging
logging.basicConfig(level=logging.WARNING)


class Command(BaseCommand):
    help = "Closes the specified poll for voting"

    def handle(self, *args, **options):
            self.stdout.write(
                self.style.SUCCESS('Starting consumer')
            )

            try:
                run_consumer()
            except KeyboardInterrupt:
                self.style.SUCCESS('Consumer stopped')


