class Rejection(Exception):
    """Stable public error; messages contain no untrusted input or credentials."""

    def __init__(self, code, message, retryable=False):
        super().__init__(message)
        self.code = code
        self.message = message
        self.retryable = retryable

    def as_dict(self):
        return {"error_code": self.code, "message": self.message,
                "retryable": self.retryable}


def require(condition, code, message):
    if not condition:
        raise Rejection(code, message)
