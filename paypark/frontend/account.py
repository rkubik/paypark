# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, flash, Markup, url_for, current_app, request
from flask_login import login_required, current_user
from . import frontend
from .forms import ChangePasswordForm, UserSettingsForm
from ..format import format_currency
from ..database import db_session


sidebar_groups = [
    [{
        'url': 'frontend.account_index',
        'name': 'My Account',
        'icon': 'user',
    }, {
        'url': 'frontend.account_settings',
        'name': 'Settings',
        'icon': 'cog',
    }, {
        'url': 'frontend.account_change_password',
        'name': 'Change Password',
        'icon': 'option-horizontal',
    }, {
        'url': 'frontend.account_add_funds',
        'name': 'Add Funds',
        'icon': 'credit-card',
    }]
]


@frontend.route('/account', methods=['GET'])
@login_required
def account_index():
    if current_user.balance <= 0:
        flash(Markup('Your account balance is 0. Click <a href="%s">here</a> to top up!' % url_for('account.add_funds')), 'danger')
    return render_template('account/index.html',
        page_title='My Account',
        page_subtitle='Current Balance $%s' % format_currency(current_user.balance),
        sidebar_groups=sidebar_groups,
    )


@frontend.route('/account/settings', methods=['GET', 'POST'])
@login_required
def account_settings():
    form = UserSettingsForm(
        [(int(x),'%s%s' % (current_app.config.get('CURRENCY_SYMBOL'), format_currency(x))) for x in current_app.config.get('ACCOUNT_TOPUP_BALANCE', [])],
        [(int(x),'%s%s' % (current_app.config.get('CURRENCY_SYMBOL'), format_currency(x))) for x in current_app.config.get('ACCOUNT_TOPUP_AMOUNT', [])],
        obj=current_user,
    )
    if form.validate_on_submit():
        form.populate_obj(current_user)
        db_session.commit()
        flash('Setting saved!', 'info')
    return render_template('account/settings.html',
        page_title='Settings',
        sidebar_groups=sidebar_groups,
        form=form,
    )


@frontend.route('/account/change_password', methods=['GET', 'POST'])
@login_required
def account_change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        current_user.change_password(form.new_password.data)
        db_session.commit()
        flash('Password changed!', 'info')
    return render_template('account/change_password.html',
        form=form,
        page_title='Change Password',
        sidebar_groups=sidebar_groups,
    )


@frontend.route('/account/add_funds', methods=['GET', 'POST'])
@login_required
def account_add_funds():
    payment_service = current_app.config.get('PAYMENT_SERVICE')
    if payment_service and payment_service == 'stripe':
        import stripe
        stripe.api_key = current_app.config.get('STRIPE_API_KEY')
        customer = stripe.Customer.create(
            email=current_user.email,
            card=request.form.get('stripeToken')
        )
        stripe.Charge.create(
            customer_id=customer.id,
            amount=1,
            currency=current_app.config.get('CURRENCY_CODE'),
            description='PayPark charge for %s %s <%s>' % (
                current_user.first_name,
                current_user.last_name,
                current_user.email,
            ),
            source='',
        )
        return render_template('account/funds_stripe.html',
            page_title='Add Funds',
            sidebar_groups=sidebar_groups,
        )
    return render_template('account/funds_no_service.html',
        page_title='Add Funds',
        sidebar_groups=sidebar_groups,
    )
