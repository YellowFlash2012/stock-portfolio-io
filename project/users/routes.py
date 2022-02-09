from . import users_blueprint
from flask import render_template, flash

@users_blueprint.route('/about', methods=['GET', 'POST'])
def about():
    return render_template('about.html', company_name='Kozuki-IO')