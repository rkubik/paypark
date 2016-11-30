# -*- coding: utf-8 -*-

import locale
import phonenumbers


def format_currency(val):
    if val:
        return locale.format('%.2f', float(val)/100, grouping=True)
    return float(0.0)    


def format_phone_number(val, country_code=None, fmt=phonenumbers.PhoneNumberFormat.INTERNATIONAL):
    return phonenumbers.format_number(
        phonenumbers.parse(val, country_code),
        fmt,
    )


def format_phone_obj(val, country_code=None):
    return val.__str__(country_code)


def format_datetime(val, fmt='%Y-%m-%d %H:%M'):
    return val.strftime(fmt)


def format_date(val, fmt='%Y-%m-%d'):
    return val.strftime(fmt)         
