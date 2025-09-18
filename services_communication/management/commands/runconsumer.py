import logging

from django.core.management import BaseCommand
from services_communication.process import run_consumer
from services_communication.consumer import message_router


logger = logging.getLogger('services_communication.consumer')


class Command(BaseCommand):
    help = "Run consumer"

    def handle(self, *args, **options):
        if not message_router._handlers and not message_router._default_handler:
            self.stdout.write(
                self.style.WARNING('No one handler registered in default message router. It\'s right?')
            )

        logger.info(
            self.style.SUCCESS('Starting consumer')
        )

        try:
            run_consumer()
        except KeyboardInterrupt:
            self.stdout.write(self.style.SUCCESS('Consumer stopped'))


