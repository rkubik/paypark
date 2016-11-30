# -*- coding: utf-8 -*-

import os


class Config:
    APP_DIR = os.path.abspath(os.path.dirname(__file__))  # this directory
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir))
    SECRET_KEY = os.environ.get(
        'SECRET_KEY',
        'fc6762171ec032ac07eae82acbaa8d523d3bdcaaf663'
    )
    LOCALE='en_US.utf8'
    COUNTRY_CODE='CA'
    CURRENCY_CODE='CAD'
    CURRENCY_SYMBOL='$'
    ACCOUNT_TOPUP_AMOUNT=[500,1000,2000,3000,5000]
    ACCOUNT_TOPUP_BALANCE=[500,1000,2000,3000,5000]
    LICENSE_PLATE_MAX=5
    LICENSE_PLATE_REGEX='^[A-Z]{3}[0-9]{3}$'
    LICENSE_PLATE_HELP='Must not contain spaces or dashes. Example: ABC123.'
    PHONE_NUMBER_MAX=3
    PHONE_NUMBER_REGEX='^1[0-9]{10}$'
    PHONE_NUMBER_HELP='Must be an 11 digit number with country code.'
    SMS_SERVICE='twilio'
    TWILIO_HOST='127.0.0.1'
    TWILIO_PORT=9000
    TWILIO_MSID='asd'

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    DB_NAME = 'development.db'
    DB_PATH = os.path.join(Config.PROJECT_ROOT, DB_NAME)
    DATABASE_URI = 'sqlite:///%s' % DB_PATH


class TestConfig(Config):
    TESTING = True
    DB_NAME = 'testing.db'
    DB_PATH = os.path.join(Config.PROJECT_ROOT, DB_NAME)
    DATABASE_URI = 'sqlite:///%s' % DB_PATH


class ProductionConfig(Config):
    DEBUG = False
    if os.environ.get('DATABASE_URI') is None:
        DB_NAME = 'production.db'
        DB_PATH = os.path.join(Config.PROJECT_ROOT, DB_NAME)
        DATABASE_URI = 'sqlite:///%s' % DB_PATH
    else:
        DATABASE_URI = os.environ['DATABASE_URI']


config = {
    'development': DevelopmentConfig,
    'testing': TestConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}

