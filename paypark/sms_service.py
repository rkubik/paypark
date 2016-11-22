# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify

from .exceptions import PayParkError, PayParkNotImplementedError, PayParkHttpError
from .commands import handle_command
from .database import db_session


class Service(object):
    def configure(self):
        raise PayParkNotImplementedError

    def run(self):
        raise PayParkNotImplementedError


class HTTPService(Service):
    def __init__(self):
        self.app = Flask(__name__)

    def run(self):
        self.app.run(host=self.host, port=self.port)
        self.app.teardown_request(self.handle_teardown_request)

    def configure(self, config):
        self.host = config.get('TWILIO_HOST')
        self.port = config.get('TWILIO_PORT')

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


class TwilioService(HTTPService):
    def __init__(self):
        super(TwilioService, self).__init__()
        self.app.add_url_rule('/', 'api',
            view_func=self.handle_request,
            methods=['POST']
        )
        self.app.register_error_handler(
            PayParkHttpError,
            self.handle_error
        )

    def configure(self, config):
        super(TwilioService, self).configure(config)
        self.mssid = config.get('TWILIO_MSSID')

    def handle_request(self):
        data = self.validate_post('Body')
        phone_number = self.validate_post('From')
        self.validate_post('MessagingServiceSid', self.mssid)
        try:
            response = handle_command(phone_number, data.split(' '))
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


SERVICES = {
    'twilio': TwilioService(),
}


def get_sms_service(config):
    '''Return SMS API service specified in configuration.

    :param config: ini config parser instance
    '''
    service = SERVICES.get(config.get('SMS_SERVICE'))
    if service:
        service.configure(config)
    else:
        raise PayParkError('SMS Service not found: %s' % config.get('SMS_SERVICE'))
    return service
