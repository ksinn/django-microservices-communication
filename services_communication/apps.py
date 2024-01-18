from django.apps import AppConfig
from services_communication.logging import get_logger

logger = get_logger('consumer')


class AppServicesCommunicationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'services_communication'

    def ready(self):
        self.load_registered_consumers()

    def load_registered_consumers(self):
        from django.conf import settings
        from django.utils.module_loading import import_module

        module_path = None
        loaded_consumers_module_count = 0
        for app in settings.INSTALLED_APPS:
            try:
                module_path = app + '.consumers'
                import_module(module_path)
                logger.info('Load consumers from %s' % module_path)
                loaded_consumers_module_count += 1
            except ImportError as e:
                if e.name == module_path:
                    continue
                raise
        if not loaded_consumers_module_count:
            logger.warning('No one module with consumers not loaded')
            return
        logger.info('Loaded {} modules with consumers'.format(loaded_consumers_module_count))

