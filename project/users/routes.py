from . import users_blueprint
from flask import render_template, abort, flash, request, current_app, redirect, url_for
from .forms import RegistrationForm
from project.models import User
from project import db
from sqlalchemy.exc import IntegrityError

@users_blueprint.route('/about', methods=['GET', 'POST'])
def about():
    return render_template('users/about.html', company_name='Kozuki-IO')

@users_blueprint.errorhandler(403)
def page_forbidden(e):
    return render_template('users/403.html'), 403

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
                flash(f'Success! Thanks for registering, {new_user.name}!')
                
                # data saved in logger
                current_app.logger.info(f'Registered new user: {form.name.data, form.email.data}!')
                
                return redirect(url_for('stocks.home'))

            except IntegrityError:
                db.session.rollback()

                # duplicate email error msg
                flash(f'Oops! This email ({form.email.data}) already exists.', 'error')
        else:
            flash(f"Something went wrong, please check the info you entered and try again!")

    return render_template('users/register.html', form=form)