# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, flash, current_app, redirect, url_for
from flask_login import current_user, login_required

from ..format import format_phone_number
from ..session import current_sessions_by_user, stop_session, start_session
from ..forms import ParkingSessionForm
from ..models import Zone, PhoneNumber
from ..tasks import topup_task


session = Blueprint('session', __name__, url_prefix='/session')
sidebar_groups = [
    [{
        'url': 'session.index',
        'name': 'Parking Session',
        'icon': 'hourglass',
    }, {
        'url': 'session.start',
        'name': 'Start New Session',
        'icon': 'plus',
    }]
]


@session.route('/', methods=['GET'])
@login_required
def index():
    current_sessions = current_sessions_by_user(current_user.id)
    return render_template('session/index.html',
        page_title='Parking Session',
        current_sessions=current_sessions,
        sidebar_groups=sidebar_groups,
    )


@session.route('/start', methods=['GET', 'POST'])
@login_required
def start():
    form = ParkingSessionForm()
    form.zone.choices = [
        (x.id, x.name) for x in Zone.query.order_by(Zone.name).all()
    ]
    form.phone_number.choices = [
        (x.id, x.__str__(current_app.config.get('COUNTRY_CODE'))) for x in PhoneNumber.query.all()
    ]
    if form.validate_on_submit():
        zone = Zone.query.filter(Zone.id==form.zone.data).first()
        phone_number = PhoneNumber.query.filter(
            PhoneNumber.id==form.phone_number.data
        ).first()
        if zone and phone_number:
            session, error = start_session(phone_number, zone)
            if session:
                flash('Session started', 'info')
            else:
                flash(error, 'danger')
        return redirect(url_for('session.index'))
    return render_template('session/start.html',
        page_title='Start New Session',
        form=form,
        sidebar_groups=sidebar_groups,
    )


@session.route('/stop/<int:id>', methods=['GET'])
@login_required
def stop(id):
    phone_number = PhoneNumber.query.filter(
        PhoneNumber.id==id,
    ).first()
    if phone_number and stop_session(phone_number):
        topup_task(phone_number.user.id)
        flash('Parking session stopped', 'info')
    return redirect(url_for('session.index'))
