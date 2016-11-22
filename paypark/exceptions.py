# -*- coding: utf-8 -*-


class PayParkError(Exception):
    pass


class PayParkBadArgError(PayParkError):
    pass


class PayParkNotImplementedError(PayParkError):
    pass


class PayParkHttpError(Exception):
    def __init__(self, message, status_code=None):
        self.message = message
        if status_code:
            self.status_code = status_code

    def to_dict(self):
        return {'error': self.message}
