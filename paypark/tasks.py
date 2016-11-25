# -*- coding: utf-8 -*-
from sqlalchemy import and_

from .session import session_payment, expired_sessions
from .models import User
from .database import db_session
from .topup import topup_user


def topup_user_task(config, user_id):
    user = User.query.filter(and_(
        User.topup==True,
        User.balance<User.topup_balance,
        User.active==True,
        User.topup_amount>0,
        User.id==user_id
    )).first()
    if not user:
        return
    topup_user(user)


def topup_users_task(config):
    users = User.query.filter(and_(
        User.topup==True,
        User.balance<User.topup_balance,
        User.active==True,
        User.topup_amount>0,
    )).all()
    for user in users:
        topup_user(user)


def session_expire_task():
    sessions = expired_sessions()
    for session in sessions:
        phone_number = PhoneNumber.query.filter(
            PhoneNumber.id==session.phone_number_id,
        ).first()
        if not phone_number:
            continue
        session.date_end = session.date_expiry
        session_payment(session, phone_number.user)
        db_session.add(session)
        db_session.add(phone_number.user)
        db_session.commit()
        topup_task(phone_record.user_id)
