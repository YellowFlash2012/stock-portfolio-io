import pytest
from project import create_app
from flask import current_app
from project import db
from project.models import Stock, User
from datetime import datetime

@pytest.fixture(scope='module')
def test_client():
    flask_app = create_app()
    flask_app.config.from_object('config.TestingConfig')
    flask_app.extensions['mail'].suppress = True #to avoid sending emails during the tests

    # Create a test client using the Flask application configured for testing
    with flask_app.test_client() as testing_client:
        # establish an app ctx be4 accessing the logger
        with flask_app.app_context():
            flask_app.logger.info('Creating database tables in test_client fixture...')
    

        yield testing_client #where the test happens



@pytest.fixture(scope='module')
def new_stock():
    stock = Stock('AAPL', '16', '406.78', 7, datetime(2022, 2, 12))
    return stock

@pytest.fixture(scope='module')
def new_user():
    user = User('geisa@email.com', 'FlaskIsAwesome123')
    return user

# to register a default user
@pytest.fixture(scope='module')
def register_default_user(test_client):
    # Register the default user
    test_client.post('/users/register',
        data={'name':'Geisa Dias', 'email': 'geisa@email.com',
        'password': 'FlaskIsAwesome123'},
        follow_redirects=True)
    return

# is default user logged in?
@pytest.fixture(scope='function')
def log_in_default_user(test_client, register_default_user):
    # Log in the default user
    test_client.post('/users/login',
    data={'email': 'geisa@email.com',
    'password': 'FlaskIsAwesome123'},
    follow_redirects=True)

    yield   # this is where the testing happens!

    # Log out the default user
    test_client.get('/users/logout', follow_redirects=True)

@pytest.fixture(scope='function')
def confirm_email_default_user(test_client, log_in_default_user):
    # Mark the user as having their email address confirmed
    user = User.query.filter_by(email='geisa@email.com').first()
    user.email_confirmed = True
    user.email_confirmed_on = datetime(2020, 7, 8)
    db.session.add(user)
    db.session.commit()

    yield user  # this is where the testing happens!

    # Mark the user as not having their email address confirmed (clean up)
    user = User.query.filter_by(email='geisa@email.com').first()
    user.email_confirmed = False
    user.email_confirmed_on = None
    db.session.add(user)
    db.session.commit()

@pytest.fixture(scope='function')
def afterwards_reset_default_user_password():
    yield  # this is where the testing happens!

    # Since a test using this fixture could change the password for the default user,
    # reset the password back to the default password
    user = User.query.filter_by(email='geisa@email.com').first()
    user.set_password('FlaskIsAwesome123')
    db.session.add(user)
    db.session.commit()

@pytest.fixture(scope='function')
def add_stocks_for_default_user(test_client, log_in_default_user):
    # Add three stocks for the default user
    test_client.post('/add_stock', data={'stock_symbol': 'SAM',
    'number_of_shares': '27',
    'purchase_price': '301.23',
    'purchase_date': '2020-07-01'})
    test_client.post('/add_stock', data={'stock_symbol': 'COST',
    'number_of_shares': '76',
    'purchase_price': '14.67',
    'purchase_date': '2019-05-26'})
    test_client.post('/add_stock', data={'stock_symbol': 'TWTR',
    'number_of_shares': '146',
    'purchase_price': '34.56',
    'purchase_date': '2020-02-03'})
    return