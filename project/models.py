from project import db

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

    def __init__(self, stock_symbol: str, number_of_shares: str, purchase_price: str):
        self.stock_symbol = stock_symbol
        self.number_of_shares = int(number_of_shares)
        self.purchase_price = float(purchase_price)

    def __repr__(self):
        return f'{self.stock_symbol} - {self.number_of_shares} shares purchased at ${self.purchase_price}'