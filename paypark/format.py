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
