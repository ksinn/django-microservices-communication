from datetime import datetime, timedelta

from services_communication.settings import communication_settings

AUTH = None


def get_alive_access_token():
    auth = get_auth()
    if (not auth) or is_access_expired(auth):
        refresh_auth()
        auth = get_auth()
    return get_access_token(auth)


def get_auth():
    return AUTH


def set_auth(auth):
    global AUTH
    AUTH = auth


def refresh_auth():
    from . import client_api_helper

    assert communication_settings.REST_API_CREDENTIAL, 'Credentional for service auth not provide. Set it in MICROSERVICES_COMMUNICATION_SETTINGS.REST_API_CREDENTIAL'
    assert communication_settings.REST_API_AUTH_URL, 'Uri for service login endpoint not provide. Set it in MICROSERVICES_COMMUNICATION_SETTINGS.REST_API_AUTH_URL'

    auth_data = client_api_helper._request(
        uri=communication_settings.REST_API_AUTH_URL,
        method='POST',
        request_formatter=client_api_helper.json_request,
        response_formatter=client_api_helper.json_response,
        json=communication_settings.REST_API_CREDENTIAL,
        no_auth=True,
    )

    set_auth(auth_data)


def get_access_token(auth):
    return auth['access_token']


def get_refresh_token(auth):
    return None
    # return auth['refresh_token']


def get_access_expire_at(auth):
    return None
    # return auth['access_expire_at']


def is_access_expired(auth):
    return False
    # return get_access_expire_at(auth) < (datetime.now() + timedelta(minutes=5))
