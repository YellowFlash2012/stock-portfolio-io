from . import stocks_blueprint
import click

from flask import current_app, render_template, request, session, flash, redirect, url_for

from flask_login import login_required, current_user
from datetime import datetime

from project.models import Stock
from project import db

# ****callbacks functions****
@stocks_blueprint.before_request
def stocks_before_request():
    current_app.logger.info('Calling before_request() for the stocks blueprint...')


@stocks_blueprint.after_request
def stocks_after_request(response):
    current_app.logger.info('Calling after_request() for the stocks blueprint...')
    return response


@stocks_blueprint.teardown_request
def stocks_teardown_request(error=None):
    current_app.logger.info('Calling teardown_request() for the stocks blueprint...')
# ***********#*********#***********

@stocks_blueprint.route('/', methods=['GET', 'POST'])
def home():
    current_app.logger.info('Calling the index() function.')
    return render_template('stocks/index.html')

# add new stock to portfolio
@stocks_blueprint.route('/add_stock', methods=['POST', 'GET'])
@login_required
def add_stock():
    if request.method == 'POST':
        new_stock = Stock(request.form['stock_symbol'], request.form['number_of_shares'], request.form['purchase_price'], current_user.id, datetime.fromisoformat(request.form['purchase_date']))

        db.session.add(new_stock)
        db.session.commit()

        # flash messages
        flash(f"You have added new stock ({request.form['stock_symbol']})!", "success")

        # log message
        current_app.logger.info(f"Added new stock ({request.form['stock_symbol']})!")

        return redirect(url_for('stocks.stocks'))
    return render_template('stocks/add_stock.html')

# list of stocks in portolio
@stocks_blueprint.route('/stocks/', methods=['GET', 'POST'])
@login_required
def stocks():
    stocks = Stock.query.order_by(Stock.id).filter_by(user_id=current_user.id).all()

    current_account_value = 0.0
    for stock in stocks:
        stock.get_stock_data()
        db.session.add(stock)
        current_account_value += stock.get_stock_position_value()

    db.session.commit()

    return render_template('stocks/stock.html', stocks = stocks, value=round(current_account_value, 2))

# custom CLI definitions
@stocks_blueprint.cli.command('create_default_set')
def create_default_set():
    """Create three new stocks and add them to the database"""
    stock1 = Stock('BLK', '100000', '247.29')
    stock2 = Stock('AVGO', '100000', '31.89')
    stock3 = Stock('ISRG', '100000', '118.77')
    db.session.add(stock1)
    db.session.add(stock2)
    db.session.add(stock3)
    db.session.commit()


@stocks_blueprint.cli.command('create')
@click.argument('symbol')
@click.argument('number_of_shares')
@click.argument('purchase_price')
def create(symbol, number_of_shares, purchase_price):
    """Create a new stock and add it to the database"""
    stock = Stock(symbol, number_of_shares, purchase_price)
    db.session.add(stock)
    db.session.commit()