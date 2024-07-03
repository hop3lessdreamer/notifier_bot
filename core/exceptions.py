""" Exceptions """


class ValidateError(BaseException):
    ...


class ResponseError(BaseException):
    ...


class OzonProductValidateError(ValidateError):
    ...


class OzonProductOutOfStock(BaseException):
    ...
