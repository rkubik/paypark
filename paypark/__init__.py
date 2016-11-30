# -*- coding: utf-8 -*-

from flask import Flask, url_for, redirect, render_template
from flask_login import LoginManager, current_user
import locale
from .api import api as api_blueprint
from .frontend import frontend as frontend_blueprint
from .database import db_session, init_engine
from .models import User, PhoneNumber, LicensePlate
from .format import format_currency, format_phone_number, format_phone_obj, format_datetime, format_date
from .config import config
from .helpers import request_wants_json


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    register_extensions(app)
    register_blueprints(app)
    register_errorhandlers(app)
    register_filters(app)
    return app


def register_extensions(app):
    app.url_map.strict_slashes = False
    init_engine(app.config.get('DATABASE_URI'))
    locale.setlocale(locale.LC_ALL, app.config.get('LOCALE'))
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


def register_blueprints(app):
    app.register_blueprint(api_blueprint)
    app.register_blueprint(frontend_blueprint)


def register_errorhandlers(app):
    def make_error_response(error):
        error_code = 500
        if hasattr(error, 'code'):
            error_code = error.code
        if request_wants_json():
            return jsonify(error={
                'code': error_code,
                'message': str(error),
            }), error.code
        return render_template('errors/%s.html' % error_code, page_title='Uh oh!'), error_code

    for error in (403, 404, 405, 500):
        app.errorhandler(error)(make_error_response)


def register_filters(app):
    @app.template_filter('currency')
    def filter_currency(val):
        return format_currency(val)

    @app.template_filter('datetime')
    def filter_datetime(val):
        return format_datetime(val)

    @app.template_filter('date')
    def filter_date(val):
        return format_date(val)

    @app.template_filter('phone')
    def filter_phone(val):
        return format_phone_number(val, app.config.get('COUNTRY_CODE'))

    @app.template_filter('phoneobj')
    def filter_phoneobj(val):
        return format_phone_obj(val, app.config.get('COUNTRY_CODE'))
