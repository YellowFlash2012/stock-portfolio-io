"""
This file (test_stocks.py) contains the functional tests for the app.py file.
"""
from app import app
import requests

from tests.conftest import *

########################
#### Helper Classes ####
########################

class MockSuccessResponse(object):
    def __init__(self, url):
        self.status_code = 200
        self.url = url
        self.headers = {'blaa': '1234'}

    def json(self):
        return {
            'Meta Data': {
                "2. Symbol": "MSFT",
                "3. Last Refreshed": "2020-03-24"
            },
            'Time Series (Daily)': {
                "2020-03-24": {
                    "4. close": "148.3400",
                },
                "2020-03-23": {
                    "4. close": "135.9800",
                }
            }
        }


class MockFailedResponse(object):
    def __init__(self, url):
        self.status_code = 404
        self.url = url
        self.headers = {'blaa': '1234'}

    def json(self):
        return {'error': 'bad'}



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

def test_monkeypatch_get_success(monkeypatch):
    """
    GIVEN a Flask application and a monkeypatched version of requests.get()
    WHEN the HTTP response is set to successful
    THEN check the HTTP response
    """
    def mock_get(url):
        return MockSuccessResponse(url)

    url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=MSFT&apikey=demo'
    monkeypatch.setattr(requests, 'get', mock_get)
    r = requests.get(url)
    assert r.status_code == 200
    assert r.url == url
    assert 'MSFT' in r.json()['Meta Data']['2. Symbol']
    assert '2022-02-10' in r.json()['Meta Data']['3. Last Refreshed']
    assert '302.3800' in r.json()['Time Series (Daily)']['2022-02-10']['4. close']

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

# ***tests related to individual stocks***
def test_get_stock_detail_page(test_client, add_stocks_for_default_user, mock_requests_get_success_weekly):
    """
    GIVEN a Flask application configured for testing, with the default user logged in
    and the default set of stocks in the database
    WHEN the '/stocks/3' page is retrieved (GET) and the response from Alpha Vantage was successful
    THEN check that the response is valid including a chart
    """
    res = test_client.get('/stocks/3', follow_redirects=True)
    assert res.status_code == 200
    assert b'Stock Details' in res.data
    assert b'canvas id="stockChart"' in res.data

def test_get_stock_detail_page_failed_response(test_client, add_stocks_for_default_user, mock_requests_get_failure):
    """
    GIVEN a Flask application configured for testing, with the default user logged in
    and the default set of stocks in the database
    WHEN the '/stocks/3' page is retrieved (GET)  but the response from Alpha Vantage failed
    THEN check that the response is valid but the chart is not displayed
    """
    res = test_client.get('/stocks/3', follow_redirects=True)
    assert res.status_code == 200
    assert b'Stock Details' in res.data
    assert b'canvas id="stockChart"' not in res.data

def test_get_stock_detail_page_incorrect_user(test_client, log_in_second_user):
    """
    GIVEN a Flask application configured for testing with the second user logged in
    WHEN the '/stocks/3' page is retrieved (GET) by the incorrect user
    THEN check that a 403 error is returned
    """
    res = test_client.get('/stocks/3')
    assert res.status_code == 403
    assert b'Stock Details' not in res.data
    assert b'canvas id="stockChart"' not in res.data

def test_get_stock_detail_page_invalid_stock(test_client, log_in_default_user):
    """
    GIVEN a Flask application configured for testing with the default user logged in
    WHEN the '/stocks/234' page is retrieved (GET)
    THEN check that a 404 error is returned
    """
    response = test_client.get('/stocks/234')
    assert response.status_code == 404
    assert b'Stock Details' not in response.data