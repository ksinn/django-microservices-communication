import logging
import os

from django.conf import settings


def get_logger(name, loggers={}, max_bytes=100*1000*1000, backup_count=3):
    if name not in loggers:

        level = getattr(settings, 'MICROSERVICES_COMMUNICATION_SETTINGS', {}).get('LOG_LEVEL')
        if not level:
            level = logging.DEBUG if settings.DEBUG else logging.WARNING

        logger = logging.Logger(name)

        LOG_ROOT = "../logs"
        if not os.path.exists(LOG_ROOT):
            os.makedirs(LOG_ROOT)
        # handler = logging.handlers.TimedRotatingFileHandler(os.path.join(LOG_ROOT, '{}.log'.format(name)), when="midnight", interval=1)
        handler = logging.handlers.RotatingFileHandler(os.path.join(settings.LOG_ROOT, '{}.log'.format(name)), maxBytes=max_bytes, backupCount=backup_count)
        handler.suffix = "%Y%m%d"
        handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s: %(funcName)s - %(levelname)s - %(message)s'))
        handler.setLevel(level)

        logger.addHandler(handler)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s: %(funcName)s - %(levelname)s - %(message)s'))
        console_handler.setLevel(level)

        logger.addHandler(console_handler)


        loggers[name] = logger

    return loggers[name]
