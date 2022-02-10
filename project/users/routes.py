from . import users_blueprint
from flask import render_template, abort

@users_blueprint.route('/about', methods=['GET', 'POST'])
def about():
    return render_template('about.html', company_name='Kozuki-IO')

@users_blueprint.errorhandler(403)
def page_forbidden(e):
    return render_template('users/403.html'), 403

@users_blueprint.route('/admin')
def admin():
    abort(403)