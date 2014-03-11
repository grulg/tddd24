__author__ = 'haeger'

import string
import random

from flask import jsonify, request, json, render_template
from geventwebsocket import WebSocketError
from werkzeug.security import generate_password_hash, check_password_hash
from TwidderServer import app
from TwidderServer.database_helper import *

# For active websockets
socket_list = dict()


@app.route("/")
def hello():
    return render_template('client.html')


@app.route("/push_message")
def push_message():
    if request.environ.get('wsgi.websocket'):
        # New socket, register in list
        ws = request.environ['wsgi.websocket']
        data = json.loads(ws.receive())
        socket_list[data['email']] = ws

        print "New socket connection: " + data['email']

        # Start listening to socket
        try:
            while True:
                message = ws.receive()

                # Has the socket died?
                if message is None:
                    del socket_list[data['email']]
                    ws.close()
                    print "Connection closed: " + data['email']
                    break

                data = json.loads(message)
                response = post_message_to_db(data['token'], data['email'], data['message']).data
                if not json.loads(response)['success']:
                    # Could not post message, just return response to client.
                    ws.send(response)
                else:
                    # Post successful, send messages to clients
                    response = get_user_messages_response(data['token'], data['email']).data
                    for socket in socket_list:
                        socket_list[socket].send(response)

        except WebSocketError as e:
            repr(e)
            print "Dead socket, removing it."
            del socket_list[data['email']]

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
        db_sign_in_user(email, token)
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

    db_sign_up(user_data)

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
    return post_message_to_db(request.form['token'], request.form['email'], request.form['message'])


def post_message_to_db(token, email, message):
    writer = db_get_user_by_token(token)
    if writer is None:
        return jsonify(success=False, message="You are not signed in.")

    reciever = db_get_user(email) if email != writer['email'] else writer
    if reciever is None:
        return jsonify(success=False, message="No such user.")

    db_post_message(message, reciever['id'], writer['id'])
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
    result = {'success': True, 'message': 'User messages retrieved', 'data': messages, 'email': email}
    return jsonify(result)
