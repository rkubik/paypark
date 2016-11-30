# -*- coding: utf-8 -*-

from flask_wtf import Form
import re
from wtforms import TextField, PasswordField, validators, SelectField, HiddenField
from flask_login import login_user, current_user
from pycountry import subdivisions
from ..models import User, LicensePlate, PhoneNumber


class LoginForm(Form):
    email = TextField('Email', [validators.Required()])
    password = PasswordField('Password', [validators.Required()])

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False
        user = User.query.filter(
            User.email == self.email.data,
        ).first()
        if not user or not user.check_password(self.password.data):
            self.email.errors.append('Email and/or password is incorrect')
            self.password.errors.append(None)
            return False
        login_user(user)
        return True


class RegisterForm(Form):
    first_name = TextField('First Name', [validators.Required()])
    last_name = TextField('Last Name', [validators.Required()])
    email = TextField('Email', [validators.Required()])
    password = PasswordField('Password', [validators.Required()])
    confirm_password = PasswordField('Confirm Password', [validators.Required(), validators.EqualTo('password', message='Passwords must match')])

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False
        user = User.query.filter(
            User.email == self.email.data,
        ).first()
        if user:
            self.email.errors.append('Email already exists in the system')
            return False
        return True


class ChangePasswordForm(Form):
    old_password = PasswordField('Current Password', [validators.Required()])
    new_password = PasswordField('New Password', [validators.Required()])
    confirm_new_password = PasswordField('Confirm Password', [validators.Required(), validators.EqualTo('new_password', message='Passwords must match')])

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False
        if not current_user.check_password(self.old_password.data):
            self.old_password.errors.append('Old password is incorrect')
            return False
        return True


class AddLicensePlateForm(Form):
    number = TextField('Plate Number', [validators.Required()])
    region = SelectField('Region')

    def __init__(self, user_id, number_max, number_regex, number_help, country_code, id=None, *args, **kwargs):
        super(AddLicensePlateForm, self).__init__(*args, **kwargs)
        self.region.choices = [(x.code.split('-')[1], x.code.split('-')[1]) for x in subdivisions.get(country_code=country_code)]
        self.id = id
        self.user_id = user_id
        self.number_max = number_max
        self.number_regex = number_regex
        self.number.description = number_help

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False
        if self.number_regex and not re.match(self.number_regex, self.number.data):
            self.number.errors.append('Invalid format')
            return False
        license_plate = LicensePlate.query.filter(
            LicensePlate.number==self.number.data
        ).first()
        if license_plate and license_plate.id != self.id:
            self.number.errors.append('License plate already exists in our system')
            return False
        total = LicensePlate.query.filter(
            LicensePlate.user_id==self.user_id,
        ).count()
        if not self.id and self.number_max and total >= self.number_max:
            self.number.errors.append('Maximum number of license plates reached: %d' % self.number_max)
            return False
        return True


class AddPhoneNumberForm(Form):
    number = TextField('Phone Number', [validators.Required()])
    nickname = TextField('Nickname')

    def __init__(self, user_id, number_max, number_regex, number_help, id=None, *args, **kwargs):
        super(AddPhoneNumberForm, self).__init__(*args, **kwargs)
        self.user_id = user_id
        self.number_max = number_max
        self.number_regex = number_regex
        self.number.description = number_help
        self.id = id

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False
        if self.number_regex and not re.match(self.number_regex, self.number.data):
            self.number.errors.append('Invalid format')
            return False
        phone_number = PhoneNumber.query.filter(
            PhoneNumber.number==self.number.data
        ).first()
        if phone_number and phone_number.id != self.id:
            self.number.errors.append('Phone number already exists in our system')
            return False
        total = PhoneNumber.query.filter(
            PhoneNumber.user_id==self.user_id,
        ).count()
        if not self.id and self.number_max and total >= self.number_max:
            self.number.errors.append('Maximum number of phone numbers reached: %d' % self.number_max)
            return False
        return True


class UserSettingsForm(Form):
    topup = SelectField('Top Up',
        description='Enable automatic top up of balance',
        choices=[(0,'Off'),(1,'On')],
        coerce=int,
    )
    topup_balance = SelectField('Top Up Balance',
        description='Top up if balance falls below this amount',
        coerce=int,
    )
    topup_amount = SelectField('Top Up Amount',
        description='Amount to top up',
        coerce=int,
    )
    topup_email = SelectField('Top Up Email',
        description='Send email when balance is topped up',
        choices=[(0,'Off'),(1,'On')],
        coerce=int,
    )

    def __init__(self, topup_balance, topup_amount, *args, **kwargs):
        super(UserSettingsForm, self).__init__(*args, **kwargs)
        self.topup_balance.choices = topup_balance
        self.topup_amount.choices = topup_amount

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False
        if self.topup.data and self.topup_balance.data <= 0:
            self.topup_balance.errors.append('Must be greater than 0')
            return False
        if self.topup.data and self.topup_amount.data <= 0:
            self.topup_amount.errors.append('Must be greater than 0')
            return False
        return True            


class ParkingSessionForm(Form):
    phone_number = SelectField('Phone Number', coerce=int)
    zone = SelectField('Zone', coerce=int)
