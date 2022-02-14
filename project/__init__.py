import os
import logging

from flask import Flask, render_template

from logging.handlers import RotatingFileHandler


from flask.logging import default_handler
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, migrate
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from flask_mail import Mail



# db config
db = SQLAlchemy()
migrate = Migrate()
csrf_protection = CSRFProtect()

# auth config
login = LoginManager()
login.login_view = "users.login"

# mail config
mail = Mail()

def create_app():
    app = Flask(__name__)

    # Configure the Flask application
    config_type = os.getenv('CONFIG_TYPE', default='config.DevelopmentConfig')
    app.config.from_object(config_type)

    
    init_ext(app)
    register_blueprints(app)
    configure_logging(app)
    register_app_callbacks(app)
    register_error_pages(app)
    return app

def register_blueprints(app):
    # import the blueprints
    from project.stocks import stocks_blueprint
    from project.users import users_blueprint

    # register the blueprints
    app.register_blueprint(stocks_blueprint)
    app.register_blueprint(users_blueprint, url_prefix='/users') #url_prefix is to indicate that all urls/routes associated with that blueprint start with /users

def configure_logging(app):
    # Logging Configuration
    if app.config['LOG_TO_STDOUT']:  # NEW!!!
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        app.logger.addHandler(stream_handler)

    else:
        file_handler = RotatingFileHandler('instance/flask-stock-portfolio.log', maxBytes=16384, backupCount=20)

        file_formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(filename)s:%(lineno)d]')
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

    # Remove the default logger configured by Flask
    app.logger.removeHandler(default_handler)

    # Log that the Flask application is starting
    app.logger.info('Starting the Kozuki-IO App...')

def register_app_callbacks(app):
    @app.before_request
    def app_before_request():
        app.logger.info('Calling before_request() for the Flask application...')

    @app.after_request
    def app_after_request(response):
        app.logger.info('Calling after_request() for the Flask application...')
        return response

    @app.teardown_request
    def app_teardown_request(error=None):
        app.logger.info('Calling teardown_request() for the Flask application...')

    @app.teardown_appcontext
    def app_teardown_appcontext(error=None):
        app.logger.info('Calling teardown_appcontext() for the Flask application...')

def register_error_pages(app):
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(403)
    def page_forbidden(e):
        return render_template('403.html'), 403

    @app.errorhandler(405)
    def method_not_allowed(e):
        return render_template('405.html'), 405

def init_ext(app):
    db.init_app(app)
    migrate.init_app(app, db)
    csrf_protection.init_app(app)
    login.init_app(app)

    # Flask-Login configuration
    from project.models import User

    @login.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    mail.init_app(app)

