import logging

from services_communication.settings import communication_settings


def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(communication_settings.LOG_LEVEL)
    return logger