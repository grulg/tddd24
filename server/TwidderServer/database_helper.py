__author__ = 'haeger'

from twidder import get_database


def db_query(query, args=(), one=False):
    cur = get_database().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


def db_insert(query, args=(), one=False):
    cur = get_database().execute(query, args)
    get_database().commit()
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


def db_get_user(email):
    if email is None:
        return None
    return db_query("SELECT * FROM user WHERE user.email = ?", (email,), True)


def db_sign_in_user(email, token):
    if email or token is None:
        return None
    return db_query("UPDATE user SET token = ? WHERE email = ?", (token, email))


def db_get_token(email):
    if email is None:
        return None
    return db_query("SELECT token FROM user WHERE email = ?", (email,), True)


def db_sign_up(user_data):
    for x in user_data:
        if x is None:
            return None
    return db_insert("INSERT INTO user (first_name, last_name, city, country, gender, email, password) VALUES (?, ?, ?, ?, ?, ?, ?)", user_data, True)


def db_get_all_tokens():
    """
    Returns all tokens in a tuple
    """
    result = db_query("SELECT token FROM user")
    tuples = ()
    for x in result:
        tuples.__add__(x)

    return tuples