# -*- coding: utf-8 -*-
from sqlalchemy import Column, Integer, String, ForeignKey, PrimaryKeyConstraint, Boolean, DateTime, Time
from sqlalchemy.orm import relationship
from werkzeug.security import check_password_hash, generate_password_hash

from .format import format_phone_number
from .database import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    password = Column(String(66), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    active = Column(Integer, nullable=False, default=1)
    admin = Column(Integer, nullable=False, default=0)
    balance = Column(Integer, nullable=False, default=0)
    phone_numbers = relationship('PhoneNumber', back_populates='user')
    license_plates = relationship('LicensePlate', back_populates='user')
    topup_email = Column(Boolean, nullable=False, default=True)
    topup = Column(Boolean, nullable=False, default=False)
    topup_balance = Column(Integer, nullable=False, default=0)
    topup_amount = Column(Integer, nullable=False, default=0)

    def __init__(self, first_name, last_name, email, password, balance=0):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.change_password(password)
        self.balance = balance

    def __repr__(self):
        return '<User %r %r %r %r %r %r %r>' % (
            self.id,
            self.first_name,
            self.last_name,
            self.email,
            self.active,
            self.admin,
            self.balance,
        )

    def is_authenticated(self):
        return True

    def is_active(self):
        return self.active

    def is_anonymous(self):
        return False

    def is_admin(self):
        return self.admin

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def change_password(self, password):
        self.password = generate_password_hash(password)

    def get_id(self):
        return self.id


class ParkingSession(Base):
    __tablename__ = 'parking_sessions'
    id = Column(Integer, primary_key=True)
    phone_number_id = Column(Integer, ForeignKey('phone_numbers.id'))
    phone_number = relationship('PhoneNumber', uselist=False)
    zone_schedule_id = Column(Integer, ForeignKey('zone_schedules.id'))
    zone_schedule = relationship('ZoneSchedule', uselist=False)
    zone_id = Column(Integer, ForeignKey('zones.id'))
    zone = relationship('Zone', uselist=False)
    date_start = Column(DateTime, nullable=False)
    date_expiry = Column(DateTime, nullable=False)
    date_end = Column(DateTime)
    amount_paid = Column(Integer, default=0)
    duration_min = Column(Integer, default=0)

    def __init__(self, phone_number_id, zone_schedule_id, zone_id, date_start, date_expiry):
        self.phone_number_id = phone_number_id
        self.zone_schedule_id = zone_schedule_id
        self.zone_id = zone_id
        self.date_start = date_start
        self.date_expiry = date_expiry

    def __repr__(self):
        return '<ParkingSessionStart %r %r %r %r %r %r>' % (
            self.id,
            self.phone_number,
            self.zone_schedule,
            self.zone,
            self.date_start,
            self.date_expiry,
        )


class PhoneNumber(Base):
    __tablename__ = 'phone_numbers'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', uselist=False)
    nickname = Column(String(20))
    number = Column(String(20), unique=True)

    def __init__(self, user_id, phone_number, nickname=None):
        self.user_id = user_id
        self.number = phone_number
        self.nickname = nickname

    def __repr__(self):
        return '<PhoneNumber %r %r %r %r>' % (
            self.id,
            self.user,
            self.number,
            self.nickname,
        )

    def __str__(self, country_code=None):
        return '%s%s' % (
            format_phone_number(self.number, country_code),
            '' if not self.nickname else ' (%s)' % self.nickname
        )


class EmailNotification(Base):
    __tablename__ = 'email_notifications'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', uselist=False)
    email = Column(String(100), nullable=False)


class SMSNotification(Base):
    __tablename__ = 'sms_notifications'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', uselist=False)
    phone_number = Column(String(20), nullable=False)


class LicensePlate(Base):
    __tablename__ = 'license_plates'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', uselist=False)
    number = Column(String(20), unique=True)
    region = Column(String(2), nullable=False)

    def __init__(self, user_id, number, region):
        self.user_id = user_id
        self.number = number
        self.region = region

    def __repr__(self):
        return '<Schedule %r %r %r %r>' % (
            self.id,
            self.user,
            self.number,
            self.region,
        )


class ZoneSchedule(Base):
    __tablename__ = 'zone_schedules'
    id = Column(Integer, primary_key=True)
    zone_group_id = Column(Integer, ForeignKey('zone_groups.id'))
    zone_group = relationship('ZoneGroup', uselist=False)
    hourly_rate = Column(Integer, nullable=False)
    max_min = Column(Integer, nullable=False)
    days = Column(String(7), nullable=False)
    time_start = Column(Time, nullable=False)
    time_end = Column(Time, nullable=False)

    def __init__(self, zone_group_id, hourly_rate, max_min, time_start, time_end, days):
        self.zone_group_id = zone_group_id
        self.hourly_rate = hourly_rate
        self.max_min = max_min
        self.time_start = time_start
        self.time_end = time_end
        self.days = days

    def __repr__(self):
        return '<ZoneSchedule %r %r %r %r %r %r %r>' % (
            self.id,
            self.zone_group,
            self.hourly_rate,
            self.max_min,
            self.time_start,
            self.time_end,
            self.days,
        )


class ZoneGroup(Base):
    __tablename__ = 'zone_groups'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)

    def __init__(self, name):
        self.name = name        

    def __repr__(self):
        return '<ZoneGroup %r %r>' % (
            self.id,
            self.name,
        )


class Zone(Base):
    __tablename__ = 'zones'
    id = Column(Integer, primary_key=True)
    zone_group_id = Column(Integer, ForeignKey('zone_groups.id'))
    zone_group = relationship('ZoneGroup', uselist=False)
    name = Column(String(50), nullable=False)
    address = Column(String(50), nullable=False)

    def __init__(self, name, address, zone_group_id):
        self.name = name
        self.address = address
        self.zone_group_id = zone_group_id

    def __repr__(self):
        return '<Zone %r %r %r %r>' % (
            self.id,
            self.name,
            self.address,
            self.zone_group,
        )
