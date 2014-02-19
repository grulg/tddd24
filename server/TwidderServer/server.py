import string
import random

from flask import Flask, jsonify, request

from database_helper import *


__author__ = 'haeger'
app = Flask(__name__)

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
    if user is None or user[6] != password:  # TODO Is there a more elegant way to get the password out of the tuple?
        return jsonify(success=False, message="Wrong username or password.", data=None)

    # Mark user as logged in by assigning token
    token = generate_token()
    db_sign_in_user(email, token)

    return jsonify(success=True, message="Successfully signed in.", data=token)


if __name__ == "__main__":
    db_init(app)
    app.run(debug=True)