import logging

from django.conf import settings


def get_logger(name):
    level = getattr(settings, 'MICROSERVICES_COMMUNICATION_SETTINGS', {}).get('LOG_LEVEL', logging.ERROR)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    return logger