# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, flash, current_app, redirect, url_for
from flask_login import current_user, login_required

from . import frontend
from ..format import format_phone_number
from ..session import current_sessions_by_user, stop_session, start_session
from ..forms import ParkingSessionForm
from ..models import Zone, PhoneNumber
from ..scheduler import scheduler


sidebar_groups = [
    [{
        'url': 'frontend.session_index',
        'name': 'Parking Session',
        'icon': 'hourglass',
    }, {
        'url': 'frontend.session_start',
        'name': 'Start New Session',
        'icon': 'plus',
    }]
]


@frontend.route('/session', methods=['GET'])
@login_required
def session_index():
    current_sessions = current_sessions_by_user(current_user.id)
    return render_template('session/index.html',
        page_title='Parking Session',
        current_sessions=current_sessions,
        sidebar_groups=sidebar_groups,
    )


@frontend.route('/session/start', methods=['GET', 'POST'])
@login_required
def session_start():
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
                flash('Parking session started in zone %s!' % (
                    zone.number,
                    'info'
                ))
            else:
                flash(error, 'danger')
        return redirect(url_for('frontend.session_index'))
    return render_template('session/start.html',
        page_title='Start New Session',
        form=form,
        sidebar_groups=sidebar_groups,
    )


@frontend.route('/session/stop/<int:id>', methods=['GET'])
@login_required
def session_stop(id):
    phone_number = PhoneNumber.query.filter(
        PhoneNumber.id==id,
    ).first()
    if phone_number and stop_session(phone_number):
        flash('Parking session stopped!', 'info')
    return redirect(url_for('frontend.session_index'))
