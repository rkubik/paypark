# -*- coding: utf-8 -*-
from sqlalchemy import and_

from .session import session_payment
from .models import User
from .database import db_session


def topup_task(user_id):
    user = User.query.filter(and_(
        User.topup==True,
        User.balance<User.topup_balance,
        User.active==True,
        User.topup_amount>0,
        User.id==user_id
    )).first()
    if not user:
        return
    # todo payment & email
    user.balance += user.topup_amount
    if user.topup_email:
        pass


def session_expire_task():
    expired_sessions = ParkingSession.query.filter(and_(
        ParkingSession.date_expiry<=date_now,
        ParkingSession.date_end==None,
    )).order_by().all()

    for expired_session in expired_sessions:
        phone_number = PhoneNumber.query.filter(
            PhoneNumber.id==expired_session.phone_number_id,
        ).first()
        if not phone_number:
            continue
        expired_session.date_end = expired_session.date_expiry
        session_payment(expired_session, phone_number.user)
        db_session.add(expired_session)
        db_session.add(phone_number.user)
        db_session.commit()
        topup_task(phone_record.user_id)
