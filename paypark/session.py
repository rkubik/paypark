# -*- coding: utf-8 -*-
from .models import ParkingSession, PhoneNumber, ZoneSchedule
from .database import db_session

from sqlalchemy import and_
from datetime import datetime, timedelta


def _current_sessions_by_phone(phone_number_id, date_now):
    return ParkingSession.query.filter(and_(
        ParkingSession.phone_number_id==phone_number_id,
        ParkingSession.date_start<=date_now,
        ParkingSession.date_expiry>=date_now,
        ParkingSession.date_end==None,
    )).order_by(ParkingSession.date_start.desc())


def current_session_by_phone(phone_number_id, date_now=None):
    if not date_now:
        date_now = datetime.now()
    return _current_sessions_by_phone(phone_number_id, date_now).first()


def current_sessions_by_phone(phone_number_id, date_now=None):
    if not date_now:
        date_now = datetime.now()
    return _current_sessions_by_phone(phone_number_id, date_now).all()


def _current_sessions_by_user(user_id, date_now):
    return ParkingSession.query.filter(and_(
        ParkingSession.phone_number.has(user_id=user_id),
        ParkingSession.date_start<=date_now,
        ParkingSession.date_expiry>=date_now,
        ParkingSession.date_end==None,
    )).order_by(ParkingSession.date_start.desc())


def current_session_by_user(user_id, date_now=None):
    if not date_now:
        date_now = datetime.now()
    return _current_sessions_by_user(user_id, date_now).first()


def current_sessions_by_user(user_id, date_now=None):
    if not date_now:
        date_now = datetime.now()
    return _current_sessions_by_user(user_id, date_now).all()


def start_session(phone_number, zone):
    date_now = datetime.now()
    if current_session_by_phone(phone_number.id, date_now=date_now):
        return None, 'Parking session already started.'
    if phone_number.user.balance <= 0:
        return None, 'Insufficient funds.'
    zone_schedule = ZoneSchedule.query.filter(and_(
        ZoneSchedule.time_start<date_now.time(),
        ZoneSchedule.time_end>date_now.time(),
        ZoneSchedule.days.contains(str(date_now.weekday())),
        ZoneSchedule.zone_group_id==zone.zone_group_id,
    )).first()
    if not zone_schedule:
        return None, 'Parking is free.'
    max_session_min = int(
        phone_number.user.balance/
        (float(zone_schedule.hourly_rate)/60)
    )
    if max_session_min <= 0:
        return None, 'Insufficient funds.'
    if max_session_min > zone_schedule.max_min:
        max_session_min = zone_schedule.max_min
    date_end = date_now + timedelta(minutes=max_session_min)
    if date_end.time() > zone_schedule.time_end:
        date_end.replace(
            hour=zone_schedule.time_end.hour,
            minute=zone_schedule.time_end.minute,
        )
    new_session = ParkingSession(
        phone_number.id,
        zone_schedule.id,
        zone.id,
        date_now,
        date_end
    )
    db_session.add(new_session)
    db_session.commit()
    return new_session, ''


def stop_session(phone_number, zone=None):
    date_now = datetime.now()
    existing_session = current_session_by_phone(
        phone_number.id,
        date_now=date_now,
    )
    if not existing_session:
        return
    if zone and existing_session.zone_id != zone.id:
        return         
    existing_session.date_end = date_now
    session_payment(existing_session, phone_number.user)
    db_session.add(existing_session)
    db_session.add(phone_number.user)
    db_session.commit()
    return existing_session


def session_payment(session, user):
    session.duration_min = int((
        session.date_end-
        session.date_start
    ).total_seconds()/60)
    session.amount_paid = (
        session.duration_min*
        session.zone_schedule.hourly_rate
    )/60
    user.balance -= session.amount_paid
