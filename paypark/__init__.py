# -*- coding: utf-8 -*-
from flask import Flask, url_for, redirect
from flask_login import LoginManager, current_user
import locale
from redis import Redis
from rq_scheduler import Scheduler

from .views.dashboard import dashboard
from .views.history import history
from .views.license_plates import license_plates
from .views.phone_numbers import phone_numbers
from .views.account import account
from .views.auth import auth
from .views.session import session
from .database import db_session
from .models import User, PhoneNumber, LicensePlate
from .format import format_currency, format_phone_number


app = Flask(__name__)
app.config.from_pyfile('../paypark.ini')
app.register_blueprint(dashboard)
app.register_blueprint(history)
app.register_blueprint(license_plates)
app.register_blueprint(phone_numbers)
app.register_blueprint(account)
app.register_blueprint(auth)
app.register_blueprint(session)

try:
    locale.setlocale(locale.LC_ALL, app.config.get('LOCALE'))
except locale.Error, e:
    pass
login_manager = LoginManager()
login_manager.init_app(app)

scheduler = Scheduler(connection=Redis())


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect(url_for('auth.login'))


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


@app.context_processor
def inject_data():
    if current_user.is_authenticated():
        return dict(
            auth_user=current_user,
            num_license_plates=len(
                LicensePlate.query.filter(
                    LicensePlate.user_id==current_user.id
                ).all()
            ),
            num_phone_numbers=len(
                PhoneNumber.query.filter(
                    PhoneNumber.user_id==current_user.id
                ).all()
            ),
        )
    return dict()


@app.template_filter('currency')
def currency(arg):
    return format_currency(arg)


@app.template_filter('date')
def date(arg, fmt='%Y-%m-%d'):
    return arg.strftime(fmt)


@app.template_filter('phone')
def phone(arg):
    return format_phone_number(arg, app.config.get('COUNTRY_CODE'))


@app.template_filter('phoneobj')
def phone_obj(arg):
    return arg.__str__(app.config.get('COUNTRY_CODE'))
