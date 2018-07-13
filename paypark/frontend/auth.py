# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import logout_user, current_user
from . import frontend
from .forms import LoginForm, RegisterForm
from ..models import User
from ..database import db_session


@frontend.route('/auth/login', methods=['GET', 'POST'])
def auth_login():
    form = LoginForm()
    if current_user.is_authenticated or form.validate_on_submit():
        return redirect(url_for('frontend.dashboard_index'))
    return render_template('auth/login.html',
        form=form,
        page_title='Login',
    )


@frontend.route('/auth/register', methods=['GET', 'POST'])
def auth_register():
    if current_user.is_authenticated:
        return redirect(url_for('frontend.dashboard_index'))
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            form.first_name.data,
            form.last_name.data,
            form.email.data,
            form.password.data,
        )
        db_session.add(user)
        db_session.commit()
        flash('Account created. Please login!', 'info')
        return redirect(url_for('frontend.auth_login'))
    return render_template('auth/register.html',
        form=form,
        page_title='Register',
    )


@frontend.route('/auth/logout')
def auth_logout():
    logout_user()
    flash('You have successfully logged out', 'info')
    return redirect(url_for('frontend.auth_login')) 
