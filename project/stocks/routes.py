from . import stocks_blueprint

from flask import current_app, render_template, request, session, flash, redirect, url_for

@stocks_blueprint.route('/', methods=['GET', 'POST'])
def home():
    current_app.logger.info('Calling the index() function.')
    return render_template('stocks/index.html')

# add new stock to portfolio
@stocks_blueprint.route('/add_stock', methods=['POST', 'GET'])
def add_stock():
    if request.method == 'POST':
        for key, value in request.form.items():
            print(f'{key}: {value}')

        # save form data to the session object
        session['stock_symbol'] = request.form['stock_symbol']
        session['number_of_shares'] = request.form['number_of_shares']
        session['purchase_price'] = request.form['purchase_price']

        # flash messages
        flash(f"You have added new stock ({request.form['stock_symbol']})!", "success")

        # log message
        current_app.logger.info(f"Added new stock ({request.form['stock_symbol']})!")

        return redirect(url_for('stocks.stocks'))
    return render_template('stocks/add_stock.html')

# list of stocks in portolio
@stocks_blueprint.route('/stocks/', methods=['GET', 'POST'])
def stocks():
    return render_template('stocks/stock.html')