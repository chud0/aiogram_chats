class AiogramChatException(Exception):
    pass


class RequestActionError(AiogramChatException):
    def __init__(self, reason, *args, **kwargs):
        self.reason = reason
        super().__init__(*args, **kwargs)


class ValidateRequestError(RequestActionError):
    pass


class CancelRequestError(RequestActionError):
    pass
