# stock-portfolio-io
Flask app for tracking stock portfolio
![stock-portfolio-io](/screenshots/stocks.png)

This project is inspired by TestDriven.io's Developing web app with python/flask course. The TDD approach is what I was really after with this project course.

# Project scope: 
TDD driven flask web app to help long term investors track their stock investment and see its performance from purchase to-date.
This is NOT for day-traders. Users sign up, verify their email, login and can add stocks to their profiles. No email verifcation, no access to the app inner functionality.

# Tech stack:
Frontend: html - css - javascript
Backend: python/flask
Database: postgreSQL
API: Alpha vantage

# key flask extensions used:
pytest
pytest-cov
flask-SQLAlchemy
Flask-Migrate
Flask-Login
Flask-Mail
freezegun
Gunicorn

# Key learning points:
1- how to use regex pattern to define an input field allowed data.

2- how to store form data into temporary session object

3 Learned about the inner working of testing with pytest, how to structure the test folder, the different kinds of tests, how to write each kind of test and how to run them.

4- learned about logging and how to configure log messages

5- The analogy between git commands and migration commands helped me understand what's going behind the hood and solidified my understand of the inner working of flask migrate.

6- Learned about flask custom CLI and how to populate db right from the command line. That's a great and handy feature!

7- Learned how to set cookie duration for auth purposes. The default duration offered by Flask_Login is 1 full year.

8- how to insert chart.js charts into a flask app

9- Deploying on heroku remains an impass for me. Something always goes wrong that I can't fix despite all my research. Will update with live preview link if I manage to deploy in the future.

![stock-portfolio-io](/screenshots/stock-detail.png)