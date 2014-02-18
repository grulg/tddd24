'''
Lesson 2,
Subject: server-side programming
Date and time: Wednesday 5th of February 2014. 10:15-12 am.
Location: VAL Seminar room, Campus Valla.
Author: Sahand Sadjadee

Revised version.
'''

# the server module provides the capability to save, get and remove phone contacts using database_helper module.

from flask import Flask
import database_helper
#more required imports

app = Flask(__name__)
app.config['DEBUG'] = True

@app.route('/')
def hello_world():
    return 'Welcome to phonebook'

@app.route('/savecontact')
def save_contact():
    # receiving firstname, familyname and phonenumber as three parameters
    # call to appropriate helper function in database_helper module

@app.route('/getcontact')
def get_contact():
    # receiving firstname, familyname as two parameters
    # call to appropriate helper function in database_helper module

@app.route('/removecontact')
def remove_contact():
    # receiving firstname, familyname as two parameters
    # call to appropriate helper function in database_helper module


@app.teardown_appcontext
def teardown_app(exception):
    #closing database using appropriate helper function in database_helper module



if __name__ == '__main__':
    app.run()

# Note: the implementation of the functions has been removed on purpose.
