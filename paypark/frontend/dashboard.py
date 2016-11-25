# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, flash
from flask_login import current_user, login_required
from sqlalchemy import and_

from . import frontend
from ..session import current_sessions_by_user
from ..models import ParkingSession, PhoneNumber


@frontend.route('/', methods=['GET'])
@login_required
def dashboard_index():
    current_sessions = current_sessions_by_user(current_user.id)
    return render_template('dashboard/index.html',
        page_title='Overview',
        current_sessions=current_sessions,
    )
