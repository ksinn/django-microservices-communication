from djangorestframework_camel_case.settings import api_settings as camel_case_api_settings
from djangorestframework_camel_case import util


def underscoreize(data):
    if not data:
        return data
    return util.underscoreize(data, **camel_case_api_settings.JSON_UNDERSCOREIZE)


def camelize(data):
    if not data:
        return data
    return util.camelize(data, **camel_case_api_settings.JSON_UNDERSCOREIZE)