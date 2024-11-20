""" Exceptions """


class ValidateError(BaseException):
    ...


class ResponseError(BaseException):
    ...


class WbApiError(ResponseError):
    ...


class OzonProductValidateError(ValidateError):
    ...


class OzonProductOutOfStock(BaseException):
    ...
