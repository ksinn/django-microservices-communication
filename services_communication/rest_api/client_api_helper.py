import requests
from django.utils.translation import get_language

from services_communication.rest_api import error
from services_communication.settings import communication_settings

from services_communication.rest_api.formatter import json_request, json_response, full_response
from services_communication.rest_api.auth_helper import get_alive_access_token

API_HOST = communication_settings.REST_API_HOST


def get(uri, request_formatter=json_request, response_formatter=json_response, **kwargs):
    return _request(uri, 'GET', request_formatter, response_formatter, **kwargs)


def post(uri, request_formatter=json_request, response_formatter=json_response, **kwargs):
    return _request(uri, 'POST', request_formatter, response_formatter, **kwargs)


def put(uri, request_formatter=json_request, response_formatter=json_response, **kwargs):
    return _request(uri, 'PUT', request_formatter, response_formatter, **kwargs)


def patch(uri, request_formatter=json_request, response_formatter=json_response, **kwargs):
    return _request(uri, 'PATCH', request_formatter, response_formatter, **kwargs)


def delete(uri, request_formatter=json_request, response_formatter=full_response, **kwargs):
    return _request(uri, 'DELETE', request_formatter, response_formatter, **kwargs)


def head(uri, request_formatter=json_request, **kwargs):
    return _request(uri, 'HEAD', request_formatter, full_response, **kwargs)


def _request(uri, method, request_formatter, response_formatter, params={}, json=None, data=None, files=None, headers=None, no_auth=False, extra_host=None, **kwargs):
    url = build_url(uri, extra_host=extra_host)

    if headers is None:
        headers = {}

    headers['Accept-Language'] = get_language()

    if not no_auth:
        headers['Authorization'] = 'Bearer ' + get_alive_access_token()

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
    except requests.exceptions.ConnectionError as e:
        raise error.RestApiConnectionError(url, method, e)
    except requests.exceptions.Timeout as e:
        raise error.RestApiTimeoutError(url, method, e)
    except requests.exceptions.RequestException as e:
        raise error.RestApiRequestError(url, method, e)

    if response.status_code // 100 != 2:
        raise build_response_error(uri, method, response)

    return response_formatter(response)


def build_url(uri, extra_host=None):
    host = extra_host if extra_host else API_HOST
    return f'{host}/{uri}'


def build_response_error(url, method, response):
    # todo: add service api error handel
    error_class = ERROR_BY_STATUS_MAP.get(response.status_code)

    if not error_class:
        if response.status_code // 100 == 4:
            error_class = error.RestApiClientError
        elif response.status_code // 100 == 5:
            error_class = error.RestApiServerError
        else:
            error_class = error.RestApiResponseWithError

    return error_class(url, method, response)


ERROR_BY_STATUS_MAP = {
    400: error.RestApiBadRequestError,
    401: error.RestApiUnauthorizedError,
    403: error.RestApiForbiddenError,
    404: error.RestApiNotFountError,
    502: error.RestApiBadGatewayError,
    504: error.RestApiGatewayTimeoutError,
}
