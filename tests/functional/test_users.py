from project import mail
from project.models import User
from itsdangerous import URLSafeTimedSerializer
from flask import current_app


# upon page load
def test_get_registration_page(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/users/register' page is requested (GET)
    THEN check the response is valid
    """
    res = test_client.get('/users/register')
    assert res.status_code == 200
    assert b'Flask Stock Portfolio App' in res.data
    assert b'User Registration' in res.data
    assert b'Name' in res.data
    assert b'Email' in res.data
    assert b'Password' in res.data

# successful sign up
def test_valid_registration(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/users/register' page is posted to (POST) with valid data
    THEN check the res is valid and the user is registered
    """

    with mail.record_messages() as outbox:
        res = test_client.post('/users/register',
        data={'name':'Geisa Dias', 'email': 'geisa@email.com',
        'password': 'FlaskIsAwesome123'},
        follow_redirects=True)
        assert res.status_code == 200
        assert b'Thanks for registering, Geisa!' in res.data
        assert b'Kozuki-IO' in res.data

        # related to flask-mail
        assert len(outbox) == 1
        assert outbox[0].subject == 'Kozuki-IO - Confirm Your Email Address'
        assert outbox[0].sender == 'kozuki.app@gmail.com'
        assert outbox[0].recipients[0] == 'geisa@email.com'
        assert 'http://localhost/users/confirm/' in outbox[0].html

# test for a missing field in the sign up form
def test_invalid_registration(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/users/register' page is posted to (POST) with invalid data (missing password)
    THEN check an error message is returned to the user
    """
    res = test_client.post('/users/register',
    data={'name':'Geisa Dias', 'email': 'patrick2@email.com',
    'password': ''},   # Empty field is not allowed!
    follow_redirects=True)
    assert res.status_code == 200
    assert b'Thanks for registering, Geisa!' not in res.data
    assert b'Flask Stock Portfolio App' in res.data
    assert b'[This field is required.]' in res.data

# check for duplicate data for unique fields
def test_duplicate_registration(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/users/register' page is posted to (POST) with the email address for an existing user
    THEN check an error message is returned to the user
    """
    test_client.post('/users/register',
    data={'name':'Geisa Dias', 'email': 'geisa@email.com',
    'password': 'FlaskIsAwesome123'},
    follow_redirects=True)
    res = test_client.post('/users/register',
    data={'name':'Geisa Dias', 'email': 'geisa@email.com',   # Duplicate email address
    'password': 'FlaskIsStillGreat!'},
    follow_redirects=True)
    assert res.status_code == 200
    assert b'Thanks for registering, geisa@email.com!' not in res.data
    assert b'Flask Stock Portfolio App' in res.data
    assert b'ERROR! Email (geisa@email.com) already exists.' in res.data

def test_get_login_page(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/users/login' page is requested (GET)
    THEN check the response is valid
    """
    res = test_client.get('/users/login')
    assert res.status_code == 200
    assert b'Login' in res.data
    assert b'Email' in res.data
    assert b'Password' in res.data
    assert b'Login' in res.data

def test_valid_login_and_logout(test_client, register_default_user):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/users/login' page is posted to (POST) with valid credentials
    THEN check the response is valid
    """
    res = test_client.post('/users/login',
    data={'email': 'geisa@email.com',
    'password': 'FlaskIsAwesome123'},
    follow_redirects=True)
    assert res.status_code == 200
    assert b'Welcome back, Geisa Dias!' in res.data
    assert b'Flask Stock Portfolio App' in res.data
    assert b'Please log in to access this page.' not in res.data

    """
    GIVEN a Flask application
    WHEN the '/users/logout' page is requested (GET) for a logged in user
    THEN check the response is valid
    """
    res = test_client.get('/users/logout', follow_redirects=True)
    assert res.status_code == 200
    assert b'See you next time!' in res.data
    assert b'Flask Stock Portfolio App' in res.data
    assert b'Please log in to access this page.' not in res.data

def test_invalid_login(test_client, register_default_user):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/users/login' page is posted to (POST) with invalid credentials (incorrect password)
    THEN check an error message is returned to the user
    """
    res = test_client.post('/users/login',
    data={'email': 'geisa@email.com',
    'password': 'FlaskIsNotAwesome'},  # Incorrect!
    follow_redirects=True)
    assert res.status_code == 200
    assert b'Invalid credentials. Try again!' in res.data
    assert b'Flask Stock Portfolio App' in res.data

def test_valid_login_when_logged_in_already(test_client, log_in_default_user):
    """
    GIVEN a Flask application configured for testing and the default user logged in
    WHEN the '/users/login' page is posted to (POST) with value credentials for the default user
    THEN check a warning is returned to the user (already logged in)
    """
    res = test_client.post('/users/login',
    data={'email': 'geisa@gmail.com',
    'password': 'FlaskIsAwesome123'},
    follow_redirects=True)
    assert res.status_code == 200
    assert b'You are already logged in!' in res.data
    assert b'Flask Stock Portfolio App' in res.data

def test_invalid_logout(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/users/logout' page is posted to (POST)
    THEN check that a 405 error is returned
    """
    res = test_client.post('/users/logout', follow_redirects=True)
    assert res.status_code == 405
    assert b'See you next time!' not in res.data
    assert b'Flask Stock Portfolio App' in res.data
    assert b'Method Not Allowed' in res.data

def test_invalid_logout_not_logged_in(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/users/logout' page is requested (GET) when the user is not logged in
    THEN check that the user is redirected to the login page
    """
    test_client.get('/users/logout', follow_redirects=True)  # Double-check that there are no logged in users!
    response = test_client.get('/users/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'Goodbye!' not in response.data
    assert b'Flask Stock Portfolio App' in response.data
    assert b'Login' in response.data
    assert b'Please log in to access this page.' in response.data

def test_user_profile_logged_in(test_client, log_in_default_user):
    """
    GIVEN a Flask application configured for testing and the default user logged in
    WHEN the '/users/profile' page is requested (GET)
    THEN check that the profile for the current user is displayed
    """
    res = test_client.get('/users/profile')
    assert res.status_code == 200
    assert b'Flask Stock Portfolio App' in res.data
    assert b'User Profile' in res.data
    assert b'Name: Sakura Chan' in res.data

def test_user_profile_not_logged_in(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/users/profile' page is requested (GET) when the user is NOT logged in
    THEN check that the user is redirected to the login page
    """
    res = test_client.get('/users/profile', follow_redirects=True)
    assert res.status_code == 200
    assert b'Flask Stock Portfolio App' in res.data
    assert b'User Profile!' not in res.data
    assert b'Name: Sakura Chan' not in res.data
    assert b'Please log in to access this page.' in res.data

def test_navigation_bar_logged_in(test_client, log_in_default_user):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET) when the user is logged in
    THEN check that the 'List Stocks', 'Add Stock', 'Profile' and 'Logout' links are present
    """
    res = test_client.get('/')
    assert res.status_code == 200
    assert b'Flask Stock Portfolio App' in res.data
    assert b'Welcome to the' in res.data
    assert b'Flask Stock Portfolio App!' in res.data
    assert b'Stocks' in res.data
    assert b'Add Stock' in res.data
    assert b'Profile' in res.data
    assert b'Logout' in res.data
    assert b'Register' not in res.data
    assert b'Login' not in res.data

def test_navigation_bar_not_logged_in(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET) when the user is not logged in
    THEN check that the 'Register' and 'Login' links are present
    """
    res = test_client.get('/')
    assert res.status_code == 200
    assert b'Flask Stock Portfolio App' in res.data
    assert b'Welcome to the' in res.data
    assert b'Flask Stock Portfolio App!' in res.data
    assert b'Register' in res.data
    assert b'Login' in res.data
    assert b'Stocks' not in res.data
    assert b'Add Stock' not in res.data
    assert b'Profile' not in res.data
    assert b'Logout' not in res.data

def test_login_with_next_valid_path(test_client, register_default_user):
    """
    GIVEN a Flask application configured for testing
    WHEN the 'users/login?next=%2Fusers%2Fprofile' page is posted to (POST) with a valid user login
    THEN check that the user is redirected to the user profile page
    """
    res = test_client.post('users/login?next=%2Fusers%2Fprofile',
    data={'email': 'geisa@email.com',
    'password': 'FlaskIsAwesome123'},
    follow_redirects=True)
    assert res.status_code == 200
    assert b'Flask Stock Portfolio App' in res.data
    assert b'User Profile' in res.data
    assert b'Email: patrick@gmail.com' in res.data

    # Log out the user - Clean up!
    test_client.get('/users/logout', follow_redirects=True)

def test_login_with_next_invalid_path(test_client, register_default_user):
    """
    GIVEN a Flask application configured for testing
    WHEN the 'users/login?next=http://www.badsite.com' page is posted to (POST) with a valid user login
    THEN check that a 400 (Bad Request) error is returned
    """
    res = test_client.post('users/login?next=http://www.badsite.com',
    data={'email': 'geisa@email.com',
    'password': 'FlaskIsAwesome123'},
    follow_redirects=True)
    assert res.status_code == 400
    assert b'User Profile' not in res.data
    assert b'Email: patrick@gmail.com' not in res.data

def test_confirm_email_valid(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/users/confirm/<token>' page is requested (GET) with valid data
    THEN check that the user's email address is marked as confirmed
    """
    # Create the unique token for confirming a user's email address
    confirm_serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    token = confirm_serializer.dumps('geisa@email.com', salt='email-confirmation-salt')

    res = test_client.get('/users/confirm/'+token, follow_redirects=True)
    assert res.status_code == 200
    assert b'Thank you for confirming your email address!' in res.data
    user = User.query.filter_by(email='geisa@email.com').first()
    assert user.email_confirmed

def test_confirm_email_already_confirmed(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/users/confirm/<token>' page is requested (GET) with valid data
    but the user's email is already confirmed
    THEN check that the user's email address is marked as confirmed
    """
    # Create the unique token for confirming a user's email address
    confirm_serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    token = confirm_serializer.dumps('geisa@gmail.com', salt='email-confirmation-salt')

    # Confirm the user's email address
    test_client.get('/users/confirm/'+token, follow_redirects=True)

    # Process a valid confirmation link for a user that has their email address already confirmed
    res = test_client.get('/users/confirm/'+token, follow_redirects=True)
    assert res.status_code == 200
    assert b'Account already confirmed.' in res.data
    user = User.query.filter_by(email='geisa@gmail.com').first()
    assert user.email_confirmed

def test_confirm_email_invalid(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/users/confirm/<token>' page is is requested (GET) with invalid data
    THEN check that the link was not accepted
    """
    res = test_client.get('/users/confirm/bad_confirmation_link', follow_redirects=True)
    assert res.status_code == 200
    assert b'The confirmation link is invalid or has expired.' in res.data