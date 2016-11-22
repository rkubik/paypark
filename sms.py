# -*- coding: utf-8 -*-
from paypark.sms_service import get_sms_service
from configobj import ConfigObj

if __name__ == '__main__':
    config = ConfigObj('paypark.ini')
    get_sms_service(config).run()
