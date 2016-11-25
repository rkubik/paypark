# -*- coding: utf-8 -*-
from paypark.sms_service import get_sms_service
from paypark.database import init_engine
from configobj import ConfigObj

if __name__ == '__main__':
    config = ConfigObj('paypark.ini')
    init_engine(config.get('DATABASE_URI'))
    get_sms_service(config).run()
