# -*- coding: utf-8 -*-
import logging
from sqlalchemy import and_
from functools import wraps
from time import mktime

from .database import db_session
from .models import PhoneNumber, Zone, ParkingSession, ZoneSchedule
from .exceptions import PayParkError
from .format import format_currency
from .session import current_session_by_phone, start_session, stop_session


logger = logging.getLogger(__name__)


def argparser(expect=0):
    '''Ensure command is called with correct number of args.

    :param f: function callback
    '''
    def actual_argparser(f):
        @wraps(f)
        def wrapper(self, args):
            if len(args) != expect:
                raise PayParkBadArgError()
            if len(args) == 1:
                args = args[0]
            return f(self, args)
        return wrapper
    return actual_argparser


class Command:
    def __init__(self, phone_number):
        self.phone_number = phone_number

    @argparser(expect=1)
    def start(self, arg):
        zone = Zone.query.filter(Zone.name==arg).first()
        if not zone:
            return 'Invalid zone.'
        session, error = start_session(self.phone_number, zone)
        if session:
            return 'Parking expires: %s.' % (
                session.date_expiry.strftime('%b %d %H:%M %p')
            )
        return error

    @argparser(expect=1)
    def end(self, arg):
        zone = Zone.query.filter(Zone.name==arg).first()
        if not zone:
            return 'Invalid zone.'
        existing_session = stop_session(self.phone_number, zone)
        if existing_session:
            return 'Parking stopped. Paid: $%s. Balance: $%s.' % (
                format_currency(existing_session.amount_paid),
                format_currency(self.phone_number.user.balance),
            )
        return 'Parking session already stopped.'

    def menu(self, args=None):
        return 'Text "START <zone>" to start parking or "END <zone>" to stop.'

    def balance(self, args=None):
        return 'Your balance is $%.2f.' % (
            format_currency(self.phone_number.user.balance)
        )


def handle_command(phone_number, args):
    logger.debug('Handle command: %s %s' % (phone_number, args))
    phone_number = PhoneNumber.query.filter(
        PhoneNumber.number==phone_number
    ).first()
    if not phone_number:
        raise PayParkError('Phone number not registered.')
    if not phone_number.user.active:
        raise PayParkError('User account not active.')
    cmd = Command(phone_number)
    try:
        return getattr(cmd, args[0].lower())(args[1:])
    except Exception, e:
        print e
#    except AttributeError, IndexError:
        return cmd.menu()
