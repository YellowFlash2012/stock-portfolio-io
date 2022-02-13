"""
This file (test_stocks.py) contains the functional tests for the app.py file.
"""
from app import app
import requests



# ***tests related to the /add_stock page***
def test_get_add_stock_page(test_client, log_in_default_user):
    """
    GIVEN a Flask application
    WHEN the '/add_stock' page is requested (GET)
    THEN check the response is valid
    """
    
    res = test_client.get('/add_stock')
    assert res.status_code == 200
    assert b'Kozuki-IO' in res.data
    assert b'Add a Stock' in res.data
    assert b'Stock Symbol <em>(required)</em>' in res.data
    assert b'Number of Shares <em>(required)</em>' in res.data
    assert b'Purchase Price ($) <em>(required)</em>' in res.data
    assert b'Purchase Date' in res.data

def test_get_add_stock_page_not_logged_in(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/add_stock' page is requested (GET) when the user is not logged in
    THEN check that the user is redirected to the login page
    """
    res = test_client.get('/add_stock', follow_redirects=True)
    assert res.status_code == 200
    assert b'Add a Stock' not in res.data
    assert b'Please log in to access this page.' in res.data

def test_post_add_stock_page(test_client, log_in_default_user, mock_requests_get_success_daily):
    """
    GIVEN a Flask application
    WHEN the '/add_stock' page is posted to (POST)
    THEN check that the user is redirected to the '/list_stocks' page
    """

    res = test_client.post('/add_stock',
    data={'stock_symbol': 'AAPL',
        'number_of_shares': '23',
        'purchase_price': '432.17', 'purchase_date': '2022-02-12'},
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
    assert b'Added new stock (AAPL)!' in res.data

def test_post_add_stock_page_not_logged_in(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/add_stock' page is posted to (POST) when the user is not logged in
    THEN check that the user is redirected to the login page
    """
    res = test_client.post('/add_stock',
    data={'stock_symbol': 'AAPL',
    'number_of_shares': '23',
    'purchase_price': '432.17',
    'purchase_date': '2022-02-12'},
    follow_redirects=True)
    assert res.status_code == 200
    assert b'List of Stocks' not in res.data
    assert b'Added new stock (AAPL)!' not in res.data
    assert b'Please log in to access this page.' in res.data

# **tests related to the list stocks page***
def test_get_stock_list_logged_in(test_client, add_stocks_for_default_user, mock_requests_get_success_daily):
    """
    GIVEN a Flask application configured for testing, with the default user logged in
    and the default set of stocks in the database
    WHEN the '/stocks' page is requested (GET)
    THEN check the response is valid and each default stock is displayed
    """
    headers = [b'Stock Symbol', b'Number of Shares', b'Purchase Price', b'Purchase Date', b'Current Share Price',
    b'Stock Position Value', b'TOTAL VALUE']
    data = [b'SAM', b'27', b'301.23', b'2020-07-01',
            b'COST', b'76', b'14.67', b'2019-05-26',
            b'TWTR', b'146', b'34.56', b'2020-02-03']

    res = test_client.get('/stocks', follow_redirects=True)
    assert res.status_code == 200
    assert b'List of Stocks' in res.data
    for header in headers:
        assert header in res.data
    for element in data:
        assert element in res.data

def test_get_stock_list_not_logged_in(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/stocks' page is requested (GET) when the user is not logged in
    THEN check that the user is redirected to the login page
    """
    res = test_client.get('/stocks', follow_redirects=True)
    assert res.status_code == 200
    assert b'List of Stocks' not in res.data
    assert b'Please log in to access this page.' in res.data



def test_monkeypatch_get_failure(monkeypatch):
    """
    GIVEN a Flask application and a monkeypatched version of requests.get()
    WHEN the HTTP response is set to failed
    THEN check the HTTP response
    """
    def mock_get(url):
        return MockFailedResponse(url)

    url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=MSFT&apikey=demo'
    monkeypatch.setattr(requests, 'get', mock_get)
    r = requests.get(url)
    print(r.json())
    assert r.status_code == 404
    assert r.url == url
    assert 'bad' in r.json()['error']