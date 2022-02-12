import pytest
from project import create_app
from flask import current_app
from project.models import Stock, User

@pytest.fixture(scope='module')
def test_client():
    flask_app = create_app()
    flask_app.config.from_object('config.TestingConfig')
    flask_app.extensions['mail'].suppress = True #to avoid sending emails during the tests

    # Create a test client using the Flask application configured for testing
    with flask_app.test_client() as testing_client:
        # establish an app ctx be4 accessing the logger
        with flask_app.app_context():
            current_app.logger.info('In the test_client() fixture...')
    

        yield testing_client #where the test happens



@pytest.fixture(scope='module')
def new_stock():
    stock = Stock('AAPL', '16', '406.78')
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