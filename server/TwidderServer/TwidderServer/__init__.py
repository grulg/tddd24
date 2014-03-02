__author__ = 'haeger'

import os
import sqlite3

from flask import Flask, g


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

import TwidderServer.view


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