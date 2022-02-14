from flask import current_app
import requests

from project import db
from werkzeug.security import generate_password_hash, check_password_hash

from datetime import datetime, timedelta

# ***daily stock price***
def create_alpha_vantage_url_daily_compact(symbol: str) -> str:
    return 'https://www.alphavantage.co/query?function={}&symbol={}&outputsize={}&apikey={}'.format(
        'TIME_SERIES_DAILY',
        symbol,
        'compact',
        current_app.config['API_KEY']
    )



# ***method to get daily stock data***
def get_current_stock_price(symbol: str) -> float:
    current_price = 0.0
    url = create_alpha_vantage_url_daily_compact(symbol)

    # Attempt the GET call to Alpha Vantage and check that a ConnectionError does
    # not occur, which happens when the GET call fails due to a network issue
    try:
        r = requests.get(url)
    except requests.exceptions.ConnectionError:
        current_app.logger.error(
            f'Error! Network problem preventing retrieving the stock data ({symbol})!')

    # Status code returned from Alpha Vantage needs to be 200 (OK) to process stock data
    if r.status_code != 200:
        current_app.logger.warning(f'Error! Received unexpected status code ({r.status_code}) '
        f'when retrieving daily stock data ({symbol})!')
        return current_price

    daily_data = r.json()

    
    if 'Time Series (Daily)' not in daily_data:
        current_app.logger.warning(f'Could not find the Time Series (Daily) key when retrieving '
        f'the daily stock data ({symbol})!')
        return current_price

    for element in daily_data['Time Series (Daily)']:
        current_price = float(daily_data['Time Series (Daily)'][element]['4. close'])
        break

    return current_price


class Stock(db.Model):
    """
    Class that represents a purchased stock in a portfolio.

    The following attributes of a stock are stored in this table:
        stock symbol (type: string)
        number of shares (type: integer)
        purchase price (type: integer)

    """

    __tablename__ = 'stocks'

    id = db.Column(db.Integer, primary_key=True)
    stock_symbol = db.Column(db.String, nullable=False)
    number_of_shares = db.Column(db.Integer, nullable=False)
    purchase_price = db.Column(db.Float, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    purchase_date = db.Column(db.DateTime)

    current_price = db.Column(db.Float)
    current_price_date = db.Column(db.DateTime)
    position_value = db.Column(db.Float)

    def __init__(self, stock_symbol: str, number_of_shares: str, purchase_price: str, user_id: int, purchase_date=None):
        self.stock_symbol = stock_symbol
        self.number_of_shares = int(number_of_shares)
        self.purchase_price = float(purchase_price)

        self.user_id = user_id

        self.purchase_date = purchase_date

        self.current_price = 0
        self.current_price_date = None
        self.position_value = 0

    def __repr__(self):
        return f'{self.stock_symbol} - {self.number_of_shares} shares purchased at ${self.purchase_price}'

    # to retrieve securities data
    def get_stock_data(self):
        if self.current_price_date is None or self.current_price_date.date() != datetime.now().date():

            current_price = get_current_stock_price(self.stock_symbol)

            if current_price > 0.0:
                self.current_price = current_price

                self.current_price_date = datetime.now()

                self.position_value = self.current_price * self.number_of_shares

                current_app.logger.debug(f'Retrieved current price {self.current_price} '
                f'for the stock data ({self.stock_symbol})!')

    def get_stock_position_value(self)-> float:
        return float(self.position_value)


    # ***weekly stock price***
    def create_alpha_vantage_get_url_weekly(self):
        return 'https://www.alphavantage.co/query?function={}&symbol={}&apikey={}'.format(
        'TIME_SERIES_WEEKLY_ADJUSTED',
        self.stock_symbol,
        current_app.config['API_KEY']
    )

    # ***method to get weekly stock data***
    def get_weekly_stock_data(self):
        title = 'Stock chart is unavailable.'
        labels = []
        values = []
        url = self.create_alpha_vantage_get_url_weekly()

        try:
            r = requests.get(url)
        except requests.exceptions.ConnectionError:
            current_app.logger.info(
                f'Error! Network problem preventing retrieving the weekly stock data ({self.stock_symbol})!')

        # Status code returned from Alpha Vantage needs to be 200 (OK) to process stock data
        if r.status_code != 200:
            current_app.logger.warning(f'Error! Received unexpected status code ({r.status_code}) '
            f'when retrieving weekly stock data ({self.stock_symbol})!')
            return title, '', ''

        weekly_data = r.json()

        # The key of 'Weekly Adjusted Time Series' needs to be present in order to process the stock data
        # Typically, this key will not be present if the API rate limit has been exceeded.
        if 'Weekly Adjusted Time Series' not in weekly_data:
            current_app.logger.warning(f'Could not find the Weekly Adjusted Time Series key when retrieving '
            f'the weekly stock data ({self.stock_symbol})!')
            return title, '', ''

        title = f'Weekly Prices ({self.stock_symbol})'

        # Determine the start date as either:
        #   - If the start date is less than 12 weeks ago, then use the date from 12 weeks ago
        #   - Otherwise, use the purchase date
        start_date = self.purchase_date
        if (datetime.now() - self.purchase_date) < timedelta(weeks=12):
            start_date = datetime.now() - timedelta(weeks=12)

        for element in weekly_data['Weekly Adjusted Time Series']:
            date = datetime.fromisoformat(element)
            if date.date() > start_date.date():
                labels.append(date)
                values.append(weekly_data['Weekly Adjusted Time Series'][element]['4. close'])

        # Reverse the elements as the data from Alpha Vantage is read in latest to oldest
        labels.reverse()
        values.reverse()

        return title, labels, values


class User(db.Model):
    """
    Class that represents a user of the application

    The following attributes of a user are stored in this table:
        * name - full name of the user
        * email - email address of the user
        * hashed password - hashed password (using werkzeug.security)

    """

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    email = db.Column(db.String, unique=True)
    password_hashed = db.Column(db.String(128))
    # set to 128 bcz password_hash is 102 characters long

    registered_on = db.Column(db.DateTime)

    email_confirmation_sent_on = db.Column(db.DateTime)

    email_confirmed = db.Column(db.Boolean, default=False)

    email_confirmed_on = db.Column(db.DateTime)

    stocks = db.relationship('Stock', backref='user', lazy='dynamic')

    def __init__(self, name: str, email: str, password_plaintext: str):
        self.name = name
        self.email = email
        self.password_hashed = self._generate_password_hash(password_plaintext)
        
        self.registered_on = datetime.now()
        self.email_confirmation_sent_on = datetime.now()
        self.email_confirmed = False
        self.email_confirmed_on = None

    def is_password_correct(self, password_plaintext: str):
        return check_password_hash(self.password_hashed, password_plaintext)

    @staticmethod
    def _generate_password_hash(password_plaintext):
        return generate_password_hash(password_plaintext)

    def __repr__(self):
        return f'<User: {self.name} {self.email}>'

    @property
    def is_authenticated(self):  
        """Return True if the user has been successfully registered."""
        return True

    @property
    def is_active(self):  
        """Always True, as all users are active."""
        return True

    @property
    def is_anonymous(self): 
        """Always False, as anonymous users aren't supported."""
        return False

    def get_id(self): 
        """Return the user ID as a unicode string (`str`)."""
        return str(self.id)

    def set_password(self, password_plaintext: str):
        self.password_hashed = self._generate_password_hash(password_plaintext)