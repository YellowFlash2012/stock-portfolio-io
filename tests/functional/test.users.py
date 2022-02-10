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
    res = test_client.post('/users/register',
    data={'name':'Geisa Dias', 'email': 'geisa@email.com',
    'password': 'FlaskIsAwesome123'},
    follow_redirects=True)
    assert res.status_code == 200
    assert b'Thanks for registering, Geisa!' in res.data
    assert b'Flask Stock Portfolio App' in res.data

# test for a missing field ij the sign up form
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