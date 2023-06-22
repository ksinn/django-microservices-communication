class SilentRaiseWrapper:

    def __init__(self, function, on_error_callback=None, on_success_callback=None):
        self._function = function
        self._on_error_callback = on_error_callback
        self._on_success_callback = on_success_callback

    def on_error(self, func):
        self._on_error_callback = func
        return self

    def on_success(self, func):
        self._on_success_callback = func
        return self

    def call(self, *args, **kwargs):
        return self(*args, **kwargs)

    def _do_on_error(self, e):
        if self._on_error_callback:
            self._on_error_callback(e)

    def _do_on_success(self, data):
        if self._on_success_callback:
            self._on_success_callback(data)

    def __call__(self, *args, **kwargs):
        try:
            res = self._function(*args, **kwargs)
        except Exception as e:
            self._do_on_error(e)
            return None, e

        self._do_on_success(res)
        return res, None
