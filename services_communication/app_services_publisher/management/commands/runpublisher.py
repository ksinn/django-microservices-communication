from django.core.management import BaseCommand
from app_services_communication.process import run_consumer


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


