from . import stocks_blueprint

from flask import current_app, render_template, request, session, flash, redirect, url_for

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
def add_stock():
    if request.method == 'POST':
        new_stock = Stock(request.form['stock_symbol'], request.form['number_of_shares'], request.form['purchase_price'])

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
def stocks():
    stocks = Stock.query.order_by(Stock.id).all()
    return render_template('stocks/stock.html', stocks = stocks)