# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, flash, current_app
from flask_login import current_user, login_required
from sqlalchemy import and_

from ..models import ParkingSession, PhoneNumber
from ..pagination import Pagination


history = Blueprint('history', __name__,  url_prefix='/history')


@history.route('/', defaults={'page': 1}, methods=['GET'])
@history.route('/page/<int:page>', methods=['GET'])
@login_required
def index(page):
    if page < 1:
        page = 1
    per_page = current_app.config.get('HISTORY_PER_PAGE', 10)
    total = ParkingSession.query.filter(and_(
        ParkingSession.phone_number.has(user_id=current_user.id),
        ParkingSession.date_end!=None,
    )).count()
    parking_sessions = ParkingSession.query.filter(and_(
        ParkingSession.phone_number.has(user_id=current_user.id),
        ParkingSession.date_end!=None,
    )).order_by(
        ParkingSession.date_start.desc()
    ).limit(per_page).offset((page-1)*per_page).all()
    pagination = Pagination(page, per_page, total, 'history.index')
    return render_template('history/index.html',
        page_title='Parking History',
        page_subtitle='(%d/%d)' % (page, pagination.pages),
        history=parking_sessions,
        pagination=pagination,
    )
