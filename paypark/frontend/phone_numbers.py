# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, flash, url_for, request, redirect, current_app, Markup
from flask_login import current_user, login_required

from . import frontend
from ..models import PhoneNumber
from ..database import db_session
from ..forms import AddPhoneNumberForm
from ..pagination import Pagination


sidebar_groups = [
    [{
        'url': 'frontend.phone_numbers_index',
        'name': 'Phone Numbers',
        'icon': 'phone',
    }, {
        'url': 'frontend.phone_numbers_add',
        'name': 'Add Phone Number',
        'icon': 'plus',
    }]
]


@frontend.route('/phone_numbers', defaults={'page': 1}, methods=['GET'])
@frontend.route('/phone_numbers/<int:page>', methods=['GET'])
@login_required
def phone_numbers_index(page):
    if page < 1:
        page = 1
    per_page = current_app.config.get('PHONE_NUMBER_PER_PAGE', 10)
    numbers = PhoneNumber.query.filter(
        PhoneNumber.user_id==current_user.id
    ).all()
    total = len(numbers)
    if total == 0:
        flash(Markup('You have no phone numbers registered. Click <a href="%s">here</a> to add one!' % url_for('phone_numbers.add')), 'danger')
    pagination = Pagination(page, per_page, total, 'frontend.phone_numbers_index')
    return render_template('phone_numbers/list.html',
        page_title='Phone Numbers',
        page_subtitle='(%d/%d)' % (page, pagination.pages),
        phone_numbers=numbers,
        sidebar_groups=sidebar_groups,
        pagination=pagination,
    )


@frontend.route('/phone_numbers/add', methods=['GET', 'POST'])
@login_required
def phone_numbers_add():
    form = AddPhoneNumberForm(
        current_user.id,
        current_app.config.get('PHONE_NUMBER_MAX'),
        current_app.config.get('PHONE_NUMBER_REGEX'),
        current_app.config.get('PHONE_NUMBER_HELP'),
    )
    if form.validate_on_submit():
        phone_number = PhoneNumber(
            current_user.id,
            form.number.data,
            nickname=form.nickname.data,
        )
        db_session.add(phone_number)
        db_session.commit()
        flash('Added phone number %s!' % phone_number.number, 'info')
        return redirect(url_for('frontend.phone_numbers_add'))
    return render_template('phone_numbers/add.html',
        page_title='Add Phone Number',
        form=form,
        sidebar_groups=sidebar_groups,
    )


@frontend.route('/phone_numbers/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def phone_numbers_edit(id):
    phone_number = PhoneNumber.query.filter(
        PhoneNumber.user_id==current_user.id,
        PhoneNumber.id==id
    ).first()
    if not phone_number:
        flash('Phone number not found!', 'danger')
        return redirect(url_for('frontend.phone_numbers_index'))
    form = AddPhoneNumberForm(
        current_user.id,
        current_app.config.get('PHONE_NUMBER_MAX'),
        current_app.config.get('PHONE_NUMBER_REGEX'),
        current_app.config.get('PHONE_NUMBER_HELP'),
        id=id,
        obj=phone_number,
    )
    if form.validate_on_submit():
        form.populate_obj(phone_number)
        db_session.add(phone_number)
        db_session.commit()
        flash('Phone number settings saved', 'info')
        return redirect(url_for('frontend.phone_numbers_edit', id=id))
    return render_template('phone_numbers/edit.html',
        page_title='Edit Phone Number',
        form=form,
        sidebar_groups=sidebar_groups,
    )


@frontend.route('/phone_numbers/remove/<int:id>', methods=['GET'])
@login_required
def phone_numbers_remove(id):
    phone_number = PhoneNumber.query.filter(
        PhoneNumber.id==id,
        PhoneNumber.user_id==current_user.id,
    ).first()
    if phone_number:
       flash('Successfully removed phone number %s!' % phone_number.number, 'info')
       db_session.delete(phone_number)
       db_session.commit()
    else:
        flash('Phone number not found!', 'danger')
    return redirect(url_for('frontend.phone_numbers_index'))
