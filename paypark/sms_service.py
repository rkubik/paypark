# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
from importlib import import_module

from .exceptions import PayParkError, PayParkNotImplementedError, PayParkHttpError
from .commands import handle_command
from .database import db_session


SERVICES = {
    'twilio': 'Twilio_Service',
    'bulksms': 'BulkSMS_Service',
}


class Service(object):
    def __init__(self, config):
        self.config = config

    def run(self):
        raise PayParkNotImplementedError


class HTTP_Service(Service):
    def __init__(self, config):
        super(HTTP_Service, self).__init__(config)
        self.app = Flask(__name__)
        self.app.register_error_handler(
            PayParkHttpError,
            self.handle_error
        )
        self.host = '127.0.0.1'
        self.port = 80

    def run(self):
        self.app.run(host=self.host, port=self.port)
        self.app.teardown_request(self.handle_teardown_request)

    def handle_error(self, error):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

    def validate_post(self, name, val=None):
        post_val = request.form.get(name)
        if not post_val:
            raise PayParkHttpError('Missing: %s' % name, 400)
        if val and post_val != val:
            raise PayParkHttpError('Bad value: %s' % name, 400)
        return post_val

    def handle_teardown_request(self):
        db_session.remove()


class Twilio_Service(HTTP_Service):
    def __init__(self, config):
        super(Twilio_Service, self).__init__(config)
        self.app.add_url_rule('/', 'Twilio Service',
            view_func=self.handle_request,
            methods=['POST']
        )
        self.host = config.get('TWILIO_HOST')
        self.port = config.get('TWILIO_PORT')
        self.mssid = config.get('TWILIO_MSSID')

    def handle_request(self):
        data = self.validate_post('Body')
        phone_number = self.validate_post('From')
        self.validate_post('MessagingServiceSid', self.mssid)
        try:
            response = handle_command(phone_number, data)
        except PayParkError, e:
            raise PayParkHttpError(str(e), 500)
        return self.handle_response(message=response)

    def handle_response(self, message=None, redirect=None):
        output = '<?xml version="1.0" encoding="UTF-8"?><Response>'
        if message:
            output += '<Message>%s</Message>' % message
        if redirect:
            output += '<Redirect>%s</Redirect>' % redirect
        return output + '</Response>'


class BulkSMS_Service(HTTP_Service):
    def __init__(self, config):
        super(BulkSMS_Service, self).__init__(config)
        self.app.add_url_rule('/', 'BulkSMS Service',
            view_func=self.handle_request,
            methods=['POST']
        )
        self.host = config.get('BULKSMS_HOST')
        self.port = config.get('BULKSMS_PORT')
        self.msisdn = config.get('BULKSMS_MSISDN')

    def handle_request(self):
        data = self.validate_post('message')
        phone_number = self.validate_post('sender')
        self.validate_post('msisdn', self.msisdn)
        try:
            response = handle_command(phone_number, data)
#            self.sms_client.send(phone_number, response)
        except PayParkError, e:
            raise PayParkHttpError(str(e), 500)
        return self.handle_response(message=response)

    def handle_response(self, message):
        return message


def get_sms_service(config):
    return getattr(
        import_module('paypark.sms_service'),
        SERVICES.get(config.get('SMS_SERVICE'))
    )(config)
