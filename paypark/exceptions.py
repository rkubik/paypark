# -*- coding: utf-8 -*-


class PayParkError(Exception):
    pass


class PayParkBadArgError(PayParkError):
    pass


class PayParkNotImplementedError(PayParkError):
    pass


class PayParkHttpError(Exception):
    def __init__(self, message, code=None):
        self.message = message
        if code:
            self.code = code

    def to_dict(self):
        return {
            'message': self.message,
            'code': self.code,
        }
