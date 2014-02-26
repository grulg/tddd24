__author__ = 'haeger'

import string
import random
import os
import sqlite3

from flask import Flask, jsonify, request, g, json
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
    return app.send_static_file('client.html')


# The following methods can hopefully be removed at some point...


@app.route("/js/client.js")
def js():
    return app.send_static_file('js/client.js')


@app.route("/css/client.css")
def css():
    return app.send_static_file('css/client.css')


@app.route("/js/serverstub.js")
def serverstub():
    return app.send_static_file('js/serverstub.js')


@app.route("/images/wimage.png")
def image():
    return app.send_static_file('images/wimage.png')

# End of stuff that should be done better...


@app.route("/socket")
def websocket_app():
    if request.environ.get('wsgi.websocket'):
        ws = request.environ['wsgi.websocket']
        try:
            while True:
                message = json.loads(ws.receive())
                # get_user_message_response returns a Response-thingy from jsonify(), so we have to choose just the data
                package = get_user_messages_response(message['token'], message['email']).data
                ws.send(package)
        except TypeError:
            print "Socket died."
    return ""


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
    token = request.form['token']
    user = db_get_user_by_token(token)
    if user is None:
        return get_user_data(token, '')
    return get_user_data(token, user['email'])


@app.route("/get_user_data_by_email", methods=['POST'])
def get_user_data_by_email():
    return get_user_data(request.form['token'], request.form['email'])


def get_user_data(token, email):
    user = db_get_user_by_token(token) if token != "" else None
    if user is None:
        return jsonify(success=False, message="You are not signed in.", data=None)

    user = db_get_user(email)
    if user is None:
        return jsonify(success=False, message="No such user.", data=None)

    user_dict = to_dict(user)
    data = {'success': True, 'message': 'User data retrieved.', 'data': user_dict}
    return jsonify(data)


def to_dict(user):
    return {'firstname': user['first_name'], 'lastname': user['last_name'], 'city': user['city'],
            'country': user['country'], 'gender': user['gender'], 'email': user['email']}


@app.route("/post_message", methods=['POST'])
def post_message():
    writer = db_get_user_by_token(request.form['token'])
    if writer is None:
        return jsonify(success=False, message="You are not signed in.")

    reciever = db_get_user(request.form['email']) if request.form['email'] != writer['email'] else writer
    if reciever is None:
        return jsonify(success=False, message="No such user.")

    db_post_message(request.form['message'], reciever['id'], writer['id'])
    return jsonify(success=True, message="Message posted.")


@app.route("/get_user_messages_by_token", methods=['POST'])
def get_user_messages_by_token():
    token = request.form['token']
    user = db_get_user_by_token(token)
    if user is None:
        return get_user_messages_response(token, '')

    return get_user_messages_response(token, user['email'])


@app.route("/get_user_messages_by_email", methods=['POST'])
def get_user_messages_by_email():
    return get_user_messages_response(request.form['token'], request.form['email'])


def get_user_messages_response(token, email):
    user = db_get_user_by_token(token)
    if user is None:
        return jsonify(success=False, message="You are not signed in.", data=None)

    reciever = db_get_user(email) if user['email'] != email else user
    if reciever is None:
        return jsonify(success=False, message="No such user.", data=None)

    messages = db_get_user_messages(reciever['id'])
    result = {'success': True, 'message': 'User messages retrieved', 'data': messages}
    return jsonify(result)


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

from TwidderServer.database_helper import *

# def the_app(environ, start_response):
#     path = environ['PATH_INFO']
#     if path == '/socket':
#         return websocket_app(environ['wsgi.socket'], start_response)
#     else:
#         return app(environ, start_response)

#if __name__ == "__main__":
 #   initialize_database()
 #   app.run(debug=True)