import os
from datetime import timedelta

class Config(object):
    FLASK_ENV = 'development'
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True

    # If the 'Remember Me' field is selected, then the user will remain logged in for an extended period of time (default value with Flask-Login is one year). 1 year being really long, it's better to set that duration to something more realistic, like 14 days:
    REMEMBER_COOKIE_DURATION = timedelta(days=14)


class ProductionConfig(Config):
    FLASK_ENV = 'production'


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False