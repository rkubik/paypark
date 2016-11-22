# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, flash, request, redirect, url_for, current_app, Markup
from flask_login import current_user, login_required

from ..models import LicensePlate
from ..database import db_session
from ..forms import AddLicensePlateForm
from ..pagination import Pagination


license_plates = Blueprint('license_plates', __name__, url_prefix='/license_plates')
sidebar_groups = [
    [{
        'url': 'license_plates.index',
        'name': 'License Plates',
        'icon': 'road',
    }, {
        'url': 'license_plates.add',
        'name': 'Add License Plate',
        'icon': 'plus',
    }]
]


@license_plates.route('/', defaults={'page': 1}, methods=['GET'])
@license_plates.route('/page/<int:page>', methods=['GET'])
@login_required
def index(page):
    if page < 1:
        page = 1
    per_page = current_app.config.get('LICENSE_PLATE_PER_PAGE', 10)
    total = LicensePlate.query.filter(
        LicensePlate.user_id==current_user.id
    ).count()
    plates = LicensePlate.query.filter(
        LicensePlate.user_id==current_user.id
    ).all()
    if len(plates) == 0:
        flash(Markup('You have no license plates registered. Click <a href="%s">here</a> to add one!' % url_for('license_plates.add')), 'danger')
    pagination = Pagination(page, per_page, total, 'license_plates.index')
    return render_template('license_plates/list.html',
        page_title='License Plates',
        page_subtitle='(%d/%d)' % (page, pagination.pages),
        license_plates=plates,
        sidebar_groups=sidebar_groups,
        pagination=pagination,
    )


@license_plates.route('/remove/<int:id>', methods=['GET'])
@login_required
def remove(id):
    license_plate = LicensePlate.query.filter(
        LicensePlate.id==id,
        LicensePlate.user_id==current_user.id,
    ).first()
    if license_plate:
        flash('Successfully removed license plate %s!' % license_plate.number, 'info')
        db_session.delete(license_plate)
        db_session.commit()
    else:
        flash('License plate not found!', 'danger')
    return redirect(url_for('license_plates.index'))


@license_plates.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    form = AddLicensePlateForm(
        current_user.id,
        current_app.config.get('LICENSE_PLATE_MAX'),
        current_app.config.get('LICENSE_PLATE_REGEX'),
        current_app.config.get('LICENSE_PLATE_HELP'),
        current_app.config.get('COUNTRY_CODE'),
    )
    if form.validate_on_submit():
        license_plate = LicensePlate(
            current_user.id,
            form.number.data,
            form.region.data,
        )
        db_session.add(license_plate)
        db_session.commit()
        flash('Added license plate %s!' % license_plate.number, 'info')
        return redirect(url_for('license_plates.add'))
    return render_template('license_plates/add.html',
        page_title='Add License Plate',
        form=form,
        sidebar_groups=sidebar_groups,
    )


@license_plates.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    license_plate = LicensePlate.query.filter(
        LicensePlate.user_id==current_user.id,
        LicensePlate.id==id
    ).first()
    if not license_plate:
        flash('License plate not found!', 'danger')
        return redirect(url_for('license_plates.index'))
    form = AddLicensePlateForm(
        current_user.id,
        current_app.config.get('LICENSE_PLATE_MAX'),
        current_app.config.get('LICENSE_PLATE_REGEX'),
        current_app.config.get('LICENSE_PLATE_HELP'),
        current_app.config.get('COUNTRY_CODE'),
        id=license_plate.id,
        obj=license_plate,
    )
    if form.validate_on_submit():
        form.populate_obj(license_plate)
        db_session.add(license_plate)
        db_session.commit()
        flash('License plate settings saved', 'info')
        return redirect(url_for('license_plates.edit', id=id))
    return render_template('license_plates/edit.html',
        page_title='Edit License Plate',
        form=form,
        sidebar_groups=sidebar_groups,
    )
