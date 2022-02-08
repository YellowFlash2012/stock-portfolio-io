"""
This file (test_app.py) contains the unit tests for the app.py file.
"""
from app import app

def test_index_page():
    """
    GIVEN a Flask application
    WHEN the '/' page is requested (GET)
    THEN check the response is valid
    """
    with app.test_client() as client:
        res = client.get('/')
        assert res.status_code == 200
        assert b'Flask Stock Portfolio App' in res.data
        assert b'Welcome to the Flask Stock Portfolio App!' in res.data

def test_about_page():
    """
    GIVEN a Flask application
    WHEN the '/about' page is requested (GET)
    THEN check the response is valid
    """
    with app.test_client() as client:
        res = client.get('/about')
        assert res.status_code == 200
        assert b'Flask Stock Portfolio App' in res.data
        assert b'About' in res.data
        assert b'This application is built using the Flask web framework.' in res.data
        assert b'Course developed by Kozuki.IO.' in res.data