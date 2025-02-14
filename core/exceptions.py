""" Exceptions """


class ValidateError(BaseException):
    ...


class ResponseError(BaseException):
    ...


class WbApiError(ResponseError):
    ...


class OzonApiError(ResponseError):
    ...


class WbProductValidateError(ValidateError):
    ...


class OzonProductValidateError(ValidateError):
    ...


class OzonProductOutOfStock(BaseException):
    ...
