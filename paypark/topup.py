# -*- coding: utf-8 -*-

def topup_email(to_email):
    pass


def topup_user(user):
    # todo payment
    user.balance += user.topup_amount
    if user.topup_email:
        topup_email(user.email)
