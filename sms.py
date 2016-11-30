# -*- coding: utf-8 -*-

import argparse
from paypark.sms_service import services
from paypark.database import init_engine
from paypark.config import config
from paypark.helpers import dict_from_class


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='PayPark SMS Application'
    )
    parser.add_argument(
        '--config',
        choices=['production','development','testing','default'],
        default='default',
        help='Configuration'
    )
    args = parser.parse_args()
    cfg = dict_from_class(config[args.config])
    init_engine(cfg.get('DATABASE_URI'))
    services[cfg.get('SMS_SERVICE')](cfg).run()
