class ValidationException(Exception):
    def __init__(self, message):
        super().__init__(message)


class IllegalArgumentError(ValueError):
    pass
