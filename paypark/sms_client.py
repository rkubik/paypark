# -*- coding: utf-8 -*-
from .exceptions import PayParkError, PayParkNotImplementedError


class Client(object):
    '''SMS Client base class.
    '''

    def configure(self, config):
        raise PayParkNotImplementedError

    def send_message(self, number, msg):
        raise PayParkNotImplementedError


class TwilioClient(Service):
    from twilio.rest import TwilioRestClient
    from twilio.exceptions import TwilioException

    def configure(self, config):
        self.number = config.get('TWILIO_NUMBER')
        self.client = TwilioRestClient(
            config.get('TWILIO_SID'),
            config.get('TWILIO_AUTH_TOKEN'),
        )

    def send_message(self, number, msg):
        try:
            message = client.messages.create(
                body=msg,
                to='+'+number,
                from_='+'+self.number,
            )
            return message.sid
        except TwilioException:
            pass


CLIENTS = {
    'twilio': TwilioClient(),
}


def get_sms_client(config):
    '''Return SMS client specified in configuration.

    :param config: ini config parser instance
    '''
    client = CLIENTS.get(config.get('SMS_CLIENT'))
    if client:
        client.configure(config)
    else:
        raisae PayParkError('SMS Client not found: %s' % config.get('SMS_CLIENT'))
    return client
