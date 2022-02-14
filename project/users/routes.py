from . import users_blueprint
from flask import render_template, abort, flash, request, current_app, redirect, url_for, copy_current_request_context
from .forms import RegistrationForm, LoginForm, EmailForm, PasswordForm, ChangePasswordForm
from flask_login import login_user, current_user, login_required, logout_user
from project.models import User

from project import db, mail
from flask_mail import Message

from sqlalchemy.exc import IntegrityError
from urllib.parse import urlparse

from threading import Thread

from itsdangerous import URLSafeTimedSerializer
from itsdangerous.exc import BadSignature
from datetime import datetime

def generate_password_reset_email(user_email):
    password_reset_serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])

    password_reset_url = url_for('users.process_password_reset_token',
    token=password_reset_serializer.dumps(user_email, salt='password-reset-salt'),
    _external=True)

    return Message(subject='Flask Stock Portfolio App - Password Reset Requested',
    html=render_template('users/email_password_reset.html', password_reset_url=password_reset_url),
    recipients=[user_email])

@users_blueprint.route('/about', methods=['GET', 'POST'])
def about():
    return render_template('users/about.html', company_name='Kozuki-IO')



@users_blueprint.route('/admin')
def admin():
    abort(403)

@users_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                new_user = User(form.name.data, form.email.data, form.password.data)
                
                db.session.add(new_user)
                
                db.session.commit()
                
                # msg in case of successful signup
                flash(f'Success! Thanks for registering, {new_user.name}! Please check your email to confirm your email address.', 'success')
                
                # data saved in logger
                current_app.logger.info(f'Registered new user: {form.name.data, form.email.data}!')

                # Send an email to the user that they have been registered - NEW!!
                @copy_current_request_context
                def send_email(message):
                    with current_app.app_context():
                        mail.send(message)

                # msg = Message(subject='Successful Sign up - Kozuki-IO App',
                # body='Our heartfelt thanks for your registration on our App! Welcome to the family',
                # recipients=[form.email.data])
                # mail.send(msg)

                msg = generate_confirmation_email(form.email.data)

                email_thread = Thread(target=send_email, args=[msg])
                email_thread.start()
                
                return redirect(url_for('users.login'))

            except IntegrityError:
                db.session.rollback()

                # duplicate email error msg
                flash(f'Oops! This email ({form.email.data}) already exists.', 'error')
        else:
            flash(f"Something went wrong, please check the info you entered and try again!")

    return render_template('users/register.html', form=form)

@users_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    # If the user is already logged in, don't allow them to try to log in again
    if current_user.is_authenticated:
        flash('Already logged in!')
        current_app.logger.info(f'Duplicate login attempt by user: {current_user.email}')
        return redirect(url_for('stocks.home'))

    form = LoginForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            
            if user and user.is_password_correct(form.password.data):
                # User's credentials have been validated, so log them in
                login_user(user, remember=form.remember_me.data)

                flash(f'Welcome back, {current_user.name}!')

                current_app.logger.info(f'Logged in user: {current_user.email}')

                # handling the next query in the URL
                if not request.args.get('next'):
                    return redirect(url_for('users.user_profile'))
                
                next_url = request.args.get('next')
                
                if urlparse(next_url).scheme != '' or urlparse(next_url).netloc != '':
                    current_app.logger.info(f'Invalid next path in login request: {next_url}')
                    logout_user()
                    return abort(400)

                current_app.logger.info(f'Redirecting after valid login to: {next_url}')

                return redirect(next_url)

        flash('Invalid credentials. Try again', 'error')
    return render_template('users/login.html', form=form)

@users_blueprint.route('/logout')
@login_required
def logout():
    current_app.logger.info(f'Logged out user: {current_user.email}')
    logout_user()
    flash('See you next time!')
    return redirect(url_for('stocks.home'))

@users_blueprint.route('/profile')
@login_required
def user_profile():
    return render_template('users/profile.html')

def generate_confirmation_email(user_email):
    confirm_serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])

    confirm_url = url_for('users.confirm_email',
    token=confirm_serializer.dumps(user_email, salt='email-confirmation-salt'),
    _external=True)

    return Message(subject='Kozuki-IO App - Confirm Your Email Address',
    html=render_template('users/email_confirmation.html', confirm_url=confirm_url),
    recipients=[user_email])

@users_blueprint.route('/confirm/<token>')
def confirm_email(token):
    try:
        confirm_serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        
        email = confirm_serializer.loads(token, salt='email-confirmation-salt', max_age=3600)
    except BadSignature:
        flash('The confirmation link is invalid or has expired.', 'error')
        current_app.logger.info(f'Invalid or expired confirmation link received from IP address: {request.remote_addr}')
        return redirect(url_for('users.login'))

    user = User.query.filter_by(email=email).first()

    if user.email_confirmed:
        flash('Account already confirmed. Please login.', 'info')
        current_app.logger.info(f'Confirmation link received for a confirmed user: {user.email}')
    else:
        user.email_confirmed = True
        user.email_confirmed_on = datetime.now()
        db.session.add(user)
        db.session.commit()

        flash('Thank you for confirming your email address!', 'success')
        current_app.logger.info(f'Email address confirmed for: {user.email}')

    return redirect(url_for('stocks.home'))

@users_blueprint.route('/password_reset_via_email', methods=['GET', 'POST'])
def password_reset_via_email():
    form = EmailForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user is None:
            flash('Error! Invalid email address!', 'error')
            return render_template('users/password_reset_via_email.html', form=form)

        if user.email_confirmed:
            @copy_current_request_context
            def send_email(email_message):
                with current_app.app_context():
                    mail.send(email_message)

            # Send an email confirming the new registration
            message = generate_password_reset_email(form.email.data)
            email_thread = Thread(target=send_email, args=[message])
            email_thread.start()

            flash('Please check your email for a password reset link.', 'success')
        else:
            flash('Your email address must be confirmed before attempting a password reset.', 'error')
        return redirect(url_for('users.login'))

    return render_template('users/password_reset_via_email.html', form=form)

@users_blueprint.route('/password_reset_via_token/<token>', methods=['GET', 'POST'])
def process_password_reset_token(token):
    try:
        password_reset_serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        email = password_reset_serializer.loads(token, salt='password-reset-salt', max_age=3600)
    except BadSignature:
        flash('The password reset link is invalid or has expired.', 'error')
        return redirect(url_for('users.login'))

    form = PasswordForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=email).first()

        if user is None:
            flash('Invalid email address!', 'error')
            return redirect(url_for('users.login'))

        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Your password has been updated!', 'success')
        return redirect(url_for('users.login'))

    return render_template('users/reset_password_with_token.html', form=form)


@users_blueprint.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()

    if form.validate_on_submit():
        if current_user.is_password_correct(form.current_password.data):
            current_user.set_password(form.new_password.data)
            
            db.session.add(current_user)
            db.session.commit()
            
            flash('Password has been updated!', 'success')
            
            current_app.logger.info(f'Password updated for user: {current_user.email}')
            
            return redirect(url_for('users.user_profile'))
        else:
            flash('ERROR! Incorrect user credentials!')
            
            current_app.logger.info(f'Incorrect password change for user: {current_user.email}')
    
    return render_template('users/change_password.html', form=form)


@users_blueprint.route('/resend_email_confirmation')
@login_required
def resend_email_confirmation():
    @copy_current_request_context
    def send_email(email_message):
        with current_app.app_context():
            mail.send(email_message)

    # Send an email to confirm the user's email address
    message = generate_confirmation_email(current_user.email)
    email_thread = Thread(target=send_email, args=[message])
    email_thread.start()

    flash('Email sent to confirm your email address.  Please check your email inbox or spam folder!', 'success')
    current_app.logger.info(f'Email re-sent to confirm email address for user: {current_user.email}')
    return redirect(url_for('users.user_profile'))