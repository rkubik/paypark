# -*- coding: utf-8 -*-

import urllib
from .exceptions import PayParkError, PayParkNotImplementedError


class Client(object):
    def send_message(self, number, msg):
        raise PayParkNotImplementedError


class Twilio_Client(Client):
    from twilio.rest import TwilioRestClient
    from twilio.exceptions import TwilioException

    def __init__(self, config):
        super(Twilio_Client, self).__init__(config)
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
        except TwilioException, e:
            raise PayParkError('Twilio Client Error: %s' % str(e))


class BulkSMS_Client(Client):
    from twilio.rest import TwilioRestClient
    from twilio.exceptions import TwilioException

    def __init__(self, config):
        super(BulkSMS_Client, self).__init__(config)
        self.eapi_url = config.get('BULKSMS_MSISDN')
        self.eapi_url = config.get('BULKSMS_EAPIURL')
        self.username = config.get('BULKSMS_USERNAME')
        self.password = config.get('BULKSMS_PASSWORD')

    def send_message(self, number, msg):
        url = '%s/submission/send_sms/2/2.0' % self.eapi_url
        params = urllib.urlencode({
            'username' : self.username,
            'password' : self.password,
            'message' : msg,
            'msisdn' : self.msisdn
        })
        f = urllib.urlopen(url, params)
        s = f.read()
        f.close() 
        result = s.split('|')
        statusCode = result[0]
        statusString = result[1]
        if statusCode != '0':
            raise PayParkError('BulkSMS Client Error: %s (%d)' % (
                statusString,
                statusCode,
            )
        return result[2]


clients = {
    'twilio': Twilio_Client,
    'bulksms': BulkSMS_Client,
}
