

from glob import escape

from flask import Flask, render_template, request, session, redirect, url_for

app=Flask(__name__)

app.secret_key = '\xcd\xbf\xf9>\t\xd4`\xa8K}\x13\xaeo\xbb\xa5\xb9^\x8e\xdc\x9c\xc2F\x8c\xdd\n\xbf\xe1JV\xefJ\x9e'

@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('index.html')

@app.route('/about', methods=['GET', 'POST'])
def about():
    return render_template('about.html', company_name='Kozuki-IO')

# list of stocks in portolio
@app.route('/stocks/', methods=['GET', 'POST'])
def stocks():
    return render_template('stock.html')

@app.route('/hello/<message>', methods=['GET', 'POST'])
def hello_message(message):
    return f"<h1>Welcome {escape(message)}</h1>"

@app.route('/blog_posts/<int:post_id>', methods=['GET', 'POST'])
def display_blog_post(post_id):
    return f"<h1>Blog Post #{post_id}...</h1>"

@app.route('/add_stock', methods=['POST', 'GET'])
def add_stock():
    if request.method == 'POST':
        for key, value in request.form.items():
            print(f'{key}: {value}')

        # save form data to the session object
        session['stock_symbol'] = request.form['stock_symbol']
        session['number_of_shares'] = request.form['number_of_shares']
        session['purchase_price'] = request.form['purchase_price']

        return redirect(url_for('stocks'))
    return render_template('add_stock.html')