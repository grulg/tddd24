__author__ = 'haeger'

import string
import random
import os
import sqlite3

from flask import Flask, jsonify, request, g
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'db/twidder.db'),
    DEBUG=True,
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('TWIDDER_SETTINGS', silent=True)


@app.route("/")
def hello():
    return "Hello World!"


def generate_token():
    tokens = db_get_all_tokens()

    while True:
        new_token = ''.join(random.choice(string.ascii_letters + string.digits) for x in range(30))

        if not tokens.__contains__(new_token):
            break

    return new_token


@app.route("/sign_in", methods=['POST'])
def sign_in():
    """
    Signs in the user and saves token to database

    :return: a json object containing success, message and data attributes
    """
    email = request.form['email']
    password = request.form['password']
    user = db_get_user(email)

    # Validate input
    if user is not None and check_password_hash(user['password'], password):
        # Mark user as logged in by assigning token
        token = generate_token()
        db_sign_in_user(email, token)   # TODO Check return value if query is okay (should be)
        return jsonify(success=True, message="Successfully signed in.", data=token)

    return jsonify(success=False, message="Wrong username or password.", data=None)


@app.route("/sign_up", methods=['POST'])
def sign_up():
    """
    Signs up a new user by saving user data to database

    :return: a json object containing success, message and data attributes
    """
    if request.form['password'] == "":
        return jsonify(success=False, message="Form data not complete.")

    # Ordering is crucial - must match database
    user_data = (request.form['firstname'], request.form['lastname'], request.form['city'],
                 request.form['country'], request.form['gender'], request.form['email'],
                 generate_password_hash(request.form['password']))

    # Check input values
    for x in user_data:
        if x is None or x == "":
            return jsonify(success=False, message="Form data not complete.")

    # Check if user already exist
    user = db_get_user(user_data[5])
    if user is not None:
        return jsonify(success=False, message="User already exists.")

    db_sign_up(user_data)   # TODO Check return value if query is okay (should be)

    return jsonify(success=True, message="Successfully created a new user.")


@app.route("/sign_out", methods=['POST'])
def sign_out():
    token = request.form['token']
    all_tokens_listed = db_get_all_tokens()

    all_tokens = list()
    for x in all_tokens_listed:
        all_tokens.append(x[0])

    if token == '' or token not in all_tokens:
        return jsonify(success=False, message="You are not signed in.")

    db_sign_out_user(token)
    return jsonify(success=True, message="Successfully signed out.")


@app.route("/change_password", methods=['POST'])
def change_password():
    token = request.form['token']
    user = db_get_user_by_token(token) if token != "" else None
    if user is None:
        return jsonify(success=False, message="You are not logged in.")

    old_password = request.form['old_password']
    if not check_password_hash(user['password'], old_password):
        return jsonify(success=False, message="Wrong password.")

    new_password = request.form['new_password']
    if new_password == "":
        return jsonify(success=False, message="New password sucks.")

    # All parameters are okay, change that password!
    db_change_password(user['email'], generate_password_hash(new_password))
    return jsonify(success=True, message="Password changed.")


@app.route("/get_user_data_by_token", methods=['POST'])
def get_user_data_by_token():
    return 'bleh'


@app.route("/get_user_data_by_email", methods=['POST'])
def get_user_data_by_email():
    token = request.form['token']
    user = db_get_user_by_token(token) if token != "" else None
    if user is None:
        return jsonify(success=False, message="You are not signed in.", data=None)

    user = db_get_user(request.form['email'])
    if user is None:
        return jsonify(success=False, message="No such user.", data=None)

    user_dict = to_dict(user)
    data = {'success': True, 'message': 'User data retrieved.', 'data': user_dict}
    return jsonify(data)


def to_dict(user):
    return {'firstname': user['first_name'], 'lastname': user['last_name'], 'city': user['city'],
            'country': user['country'], 'gender': user['gender'], 'email': user['email']}


def db_connect():
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


@app.teardown_appcontext
def close_database_connection(error):
    """
     Closes the database again at the end of the request
    """
    if hasattr(g, 'db'):
        g.db.close()


def get_database():
    """
    Opens a new database connection if there is none yet for the current
    application context.
    """
    if not hasattr(g, 'db'):
        g.db = db_connect()
    return g.db


def initialize_database():
    with app.app_context():
        db = get_database()
        with app.open_resource('db/schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

from database_helper import *

if __name__ == "__main__":
    initialize_database()
    app.run(debug=True)