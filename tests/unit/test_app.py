"""
This file (test_app.py) contains the unit tests for the app.py file.
"""

def test_index_page(test_client):
    """
    GIVEN a Flask application
    WHEN the '/' page is requested (GET)
    THEN check the response is valid
    """
    
    res = test_client.get('/')
    assert res.status_code == 200
    assert b'Flask Stock Portfolio App' in res.data
    assert b'Welcome to the' in res.data 
    assert b'Flask Stock Portfolio App!' in res.data

def test_about_page(test_client):
    """
    GIVEN a Flask application
    WHEN the '/about' page is requested (GET)
    THEN check the response is valid
    """
    
    res = test_client.get('/users/about')
    assert res.status_code == 200
    assert b'Flask Stock Portfolio App' in res.data
    assert b'About' in res.data
    assert b'This application is built using the Flask web framework.' in res.data
    assert b'Course developed by Kozuki.IO.' in res.data