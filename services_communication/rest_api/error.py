
class RestApiError(Exception):

    def __init__(self, message):
        super().__init__(message)
        self.message = message


class RestApiRequestError(RestApiError):

    def __init__(self, url, method, e, *args, **kwargs):
        super().__init__("Request to {} {} rice error {}".format(method, url, e))


class RestApiConnectionError(RestApiRequestError):
    pass


class RestApiTimeoutError(RestApiRequestError):
    pass


class RestApiResponseWithError(RestApiError):

    def __init__(self, url, method, response, *args, **kwargs):
        super().__init__("Endpoint {} {} response with {}:{}".format(method, url, response.status_code, response.text))
        self.status_code = response.status_code
        try:
            self.response_body = response.json()
            self.has_response_body = True
        except:
            self.response_body = {}
            self.has_response_body = False


class RestApiServerError(RestApiResponseWithError):
    pass


class RestApiBadGatewayError(RestApiServerError):
    pass


class RestApiGatewayTimeoutError(RestApiServerError):
    pass


class RestApiClientError(RestApiResponseWithError):
    pass


class RestApiBadRequestError(RestApiClientError):
    pass


class RestApiUnauthorizedError(RestApiClientError):
    pass


class RestApiForbiddenError(RestApiClientError):
    pass


class RestApiNotFountError(RestApiClientError):
    pass
