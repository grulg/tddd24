import sqlite3

from flask import g

__author__ = 'haeger'

DATABASE = 'db/twidder.db'


def db_connect():
    return sqlite3.connect(DATABASE)


def db_close():
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


def db_get():
    db = getattr(g, 'db', None)
    if db is None:
        db = g.db = db_connect()
    return db


def db_init(app):
    with app.app_context():
        db = db_get()
        with app.open_resource('db/schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


def db_query(query, args=(), one=False):
    cur = db_get().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


def db_get_user(email):
    return db_query("SELECT * FROM user WHERE user.email = ?", (email,), True)


def db_sign_in_user(email, token):
    return db_query("UPDATE user SET token = ? WHERE email = ?", (token, email))


def db_get_token(email):
    return db_query("SELECT token FROM user WHERE email = ?", (email,), True)


def db_get_all_tokens():
    """
    Returns all tokens in a tuple
    """
    result = db_query("SELECT token FROM user")
    tuples = ()
    for x in result:
        tuples.__add__(x)

    return tuples



