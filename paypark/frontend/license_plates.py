# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, flash, request, redirect, url_for, current_app, Markup
from flask_login import current_user, login_required

from . import frontend
from ..models import LicensePlate
from ..database import db_session
from ..forms import AddLicensePlateForm
from ..pagination import Pagination


sidebar_groups = [
    [{
        'url': 'frontend.license_plates_index',
        'name': 'License Plates',
        'icon': 'road',
    }, {
        'url': 'frontend.license_plates_add',
        'name': 'Add License Plate',
        'icon': 'plus',
    }]
]


@frontend.route('/license_plates', defaults={'page': 1}, methods=['GET'])
@frontend.route('/license_plates/page/<int:page>', methods=['GET'])
@login_required
def license_plates_index(page):
    if page < 1:
        page = 1
    per_page = current_app.config.get('LICENSE_PLATE_PER_PAGE', 10)
    plates = LicensePlate.query.filter(
        LicensePlate.user_id==current_user.id
    ).all()
    total = len(plates)
    if total == 0:
        flash(Markup('You have no license plates registered. Click <a href="%s">here</a> to add one!' % url_for('frontend.license_plates_add')), 'danger')
    pagination = Pagination(page, per_page, total, 'frontend.license_plates_index')
    return render_template('license_plates/list.html',
        page_title='License Plates',
        page_subtitle='(%d/%d)' % (page, pagination.pages),
        license_plates=plates,
        sidebar_groups=sidebar_groups,
        pagination=pagination,
    )


@frontend.route('/license_plates/remove/<int:id>', methods=['GET'])
@login_required
def license_plates_remove(id):
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
    return redirect(url_for('frontend.license_plates_index'))


@frontend.route('/license_plates/add', methods=['GET', 'POST'])
@login_required
def license_plates_add():
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
        return redirect(url_for('frontend.license_plates_add'))
    return render_template('license_plates/add.html',
        page_title='Add License Plate',
        form=form,
        sidebar_groups=sidebar_groups,
    )


@frontend.route('/license_plates/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def license_plates_edit(id):
    license_plate = LicensePlate.query.filter(
        LicensePlate.user_id==current_user.id,
        LicensePlate.id==id
    ).first()
    if not license_plate:
        flash('License plate not found!', 'danger')
        return redirect(url_for('frontend.license_plates_index'))
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
        return redirect(url_for('frontend.license_plates_edit', id=id))
    return render_template('license_plates/edit.html',
        page_title='Edit License Plate',
        form=form,
        sidebar_groups=sidebar_groups,
    )
