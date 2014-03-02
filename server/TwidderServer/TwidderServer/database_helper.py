__author__ = 'haeger'

from TwidderServer.__init__ import get_database


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


def db_get_user_by_token(token):
    if token is None:
        return None
    return db_query("SELECT * FROM user WHERE token = ?", (token,), True)


def db_sign_in_user(email, token):
    if email is None or token is None:
        return None
    return db_insert("UPDATE user SET token = ? WHERE email = ?", (token, email))


def db_sign_out_user(token):
    if token is None:
        return None
    return db_insert("UPDATE user SET token = null WHERE token = ?", (token,))


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
    return db_query("SELECT token FROM user")


def db_change_password(email, new_password):
    return db_insert("UPDATE user SET password = ? WHERE email = ?", (new_password, email))


def db_post_message(message, reciever_id, writer_id):
    return db_insert("INSERT INTO message (reciever, writer, content) VALUES (?, ?, ?)", (reciever_id, writer_id, message))


def db_get_user_messages(reciever_id):
    data = db_query("SELECT DISTINCT u.email, m.content FROM message m, user u WHERE m.reciever = ? AND m.writer = u.id ORDER BY m.id DESC", (reciever_id,))
    result = list()
    for row in data:
        result.append({'writer': row['email'], 'content': row['content']})

    return result