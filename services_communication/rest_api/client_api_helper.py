import requests
from services_communication.settings import communication_settings

from services_communication.rest_api.formatter import json_request, json_response, full_response
from services_communication.rest_api.auth_helper import get_alive_access_token

API_HOST = communication_settings.REST_API_HOST


def get(uri, request_formatter=json_request, response_formatter=json_response, **kwargs):
    return _request(uri, 'GET', request_formatter, response_formatter, **kwargs)


def post(uri, request_formatter=json_request, response_formatter=json_response, **kwargs):
    return _request(uri, 'POST', request_formatter, response_formatter, **kwargs)


def delete(uri, request_formatter=json_request, response_formatter=full_response, **kwargs):
    return _request(uri, 'DELETE', request_formatter, response_formatter, **kwargs)


def head(uri, request_formatter=json_request, **kwargs):
    return _request(uri, 'HEAD', request_formatter, full_response, **kwargs)


def _request(uri, method, request_formatter, response_formatter, params={}, json=None, data=None, files=None, headers=None, no_auth=False, **kwargs):
    url = build_url(uri)

    if headers is None:
        headers = {}

    if not no_auth:
        headers['Authorization'] = get_alive_access_token()

    try:
        response = requests.request(
            method,
            url,
            headers=headers,

            params=request_formatter(params),
            json=request_formatter(json),
            data=request_formatter(data),
            files=files,
            **kwargs,
        )
    except Exception as e:
        raise raise_exception(url, method, e)

    if response.status_code / 100 != 2:
        raise_error(uri, method, response)

    return response_formatter(response)


def build_url(uri):
    return f'{API_HOST}/{uri}'


def raise_error(url, method, response):
    # todo: add service api error handel
    # error_class = ERROR_BY_STATUS_MAP.get(response.status_code, ServiceReturnError)
    error_class = ERROR_BY_STATUS_MAP.get(response.status_code, Exception)
    raise error_class("Request to {} {} response with {}:{}".format(url, method, response.status_code, response.text))


def raise_exception(url, method, e):
    raise Exception("Request to {} {} rice error {}".format(url, method, e))


ERROR_BY_STATUS_MAP = {
    # 400: ServiceReturnBadRequest,
    # 404: ServiceReturnNotFound,
    # 500: ServiceReturnInternalServerError,
}
