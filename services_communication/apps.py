from django.apps import AppConfig
from services_communication.logging import get_logger
logger = get_logger(__name__)


class AppServicesCommunicationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'services_communication'

    def ready(self):
        self.load_registered_consumers()

    def load_registered_consumers(self):
        from django.conf import settings
        from django.utils.module_loading import import_module

        for app in settings.INSTALLED_APPS:
            try:
                module_path = app + '.consumers'
                import_module(module_path)
                logger.info('Load consumers from %s' % module_path)
            except ImportError as e:
                pass

