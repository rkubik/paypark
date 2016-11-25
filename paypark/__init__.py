# -*- coding: utf-8 -*-
from flask import Flask, url_for, redirect
from flask_login import LoginManager, current_user
import locale

from .api import api as api_blueprint
from .frontend import frontend as frontend_blueprint
from .database import db_session, init_engine
from .models import User, PhoneNumber, LicensePlate
from .format import format_currency, format_phone_number


app = Flask(__name__)
app.config.from_pyfile('../paypark.ini')
app.url_map.strict_slashes = False
app.register_blueprint(api_blueprint)
app.register_blueprint(frontend_blueprint)

init_engine(app.config.get('DATABASE_URI'))

try:
    locale.setlocale(locale.LC_ALL, app.config.get('LOCALE'))
except locale.Error, e:
    pass
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect(url_for('frontend.auth_login'))


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
def date(arg, fmt='%Y-%m-%d %H:%M'):
    return arg.strftime(fmt)


@app.template_filter('phone')
def phone(arg):
    return format_phone_number(arg, app.config.get('COUNTRY_CODE'))


@app.template_filter('phoneobj')
def phone_obj(arg):
    return arg.__str__(app.config.get('COUNTRY_CODE'))
