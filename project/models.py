from project import db
from werkzeug.security import generate_password_hash, check_password_hash

from datetime import datetime

class Stock(db.Model):
    """
    Class that represents a purchased stock in a portfolio.

    The following attributes of a stock are stored in this table:
        stock symbol (type: string)
        number of shares (type: integer)
        purchase price (type: integer)

    Note: Due to a limitation in the data types supported by SQLite, the purchase price is stored as an integer:
    $24.10 -> 2410
    $100.00 -> 10000
    $87.65 -> 8765
    """

    __tablename__ = 'stocks'

    id = db.Column(db.Integer, primary_key=True)
    stock_symbol = db.Column(db.String, nullable=False)
    number_of_shares = db.Column(db.Integer, nullable=False)
    purchase_price = db.Column(db.Float, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    purchase_date = db.Column(db.DateTime)

    def __init__(self, stock_symbol: str, number_of_shares: str, purchase_price: str, user_id: int, purchase_date=None):
        self.stock_symbol = stock_symbol
        self.number_of_shares = int(number_of_shares)
        self.purchase_price = float(purchase_price)

        self.user_id = user_id

        self.purchase_date = purchase_date

    def __repr__(self):
        return f'{self.stock_symbol} - {self.number_of_shares} shares purchased at ${self.purchase_price}'


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