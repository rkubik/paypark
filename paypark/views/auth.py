# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import logout_user, current_user

from ..forms import LoginForm, RegisterForm
from ..models import User
from ..database import db_session


auth = Blueprint('auth', __name__,  url_prefix='/auth')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if current_user.is_authenticated() or form.validate_on_submit():
        return redirect(url_for('dashboard.index'))
    return render_template('auth/login.html',
        form=form,
        page_title='Login',
    )


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated():
        return redirect(url_for('dashboard.index'))
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
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html',
        form=form,
        page_title='Register',
    )


@auth.route('/logout')
def logout():
    logout_user()
    flash('You have successfully logged out', 'info')
    return redirect(url_for('auth.login')) 
