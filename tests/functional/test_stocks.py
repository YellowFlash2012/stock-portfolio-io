"""
This file (test_stocks.py) contains the functional tests for the app.py file.
"""
from app import app


def test_get_add_stock_page(test_client):
    """
    GIVEN a Flask application
    WHEN the '/add_stock' page is requested (GET)
    THEN check the response is valid
    """
    
    res = test_client.get('/add_stock')
    assert res.status_code == 200
    assert b'Flask Stock Portfolio App' in res.data
    assert b'Add a Stock' in res.data
    assert b'Stock Symbol <em>(required)</em>' in res.data
    assert b'Number of Shares <em>(required)</em>' in res.data
    assert b'Purchase Price ($) <em>(required)</em>' in res.data

def test_post_add_stock_page(test_client):
    """
    GIVEN a Flask application
    WHEN the '/add_stock' page is posted to (POST)
    THEN check that the user is redirected to the '/list_stocks' page
    """

    res = test_client.post('/add_stock',
    data={'stock_symbol': 'AAPL',
        'number_of_shares': '23',
        'purchase_price': '432.17'},
        follow_redirects=True)
        # follow_redirects is in reference to return redirect(url_for('list_stocks'))
        
    assert res.status_code == 200
    assert b'List of Stocks' in res.data
    assert b'Stock Symbol' in res.data
    assert b'Number of Shares' in res.data
    assert b'Purchase Price' in res.data
    assert b'AAPL' in res.data
    assert b'23' in res.data
    assert b'432.17' in res.data