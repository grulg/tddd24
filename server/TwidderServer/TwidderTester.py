from TwidderServer import twidder

__author__ = 'haeger'
import os
import unittest
import tempfile

from flask import json

class TwidderTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, twidder.app.config['DATABASE'] = tempfile.mkstemp()
        twidder.app.config['TESTING'] = True
        self.app = twidder.app.test_client()
        twidder.initialize_database()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(twidder.app.config['DATABASE'])

    # Sending any parameter as 'None' will result in
    # HTTP error code 400 'Bad Request', and is therefore
    # not tested

    def test_sign_in(self):
        # Invalid sign in: bad data
        rv = self.sign_in('', '')
        assert not rv['success']
        assert 'Wrong username or password.' in rv['message']
        assert rv['data'] is None

        rv = self.sign_in('me@haeger.me', '')
        assert not rv['success']
        assert 'Wrong username or password.' in rv['message']
        assert rv['data'] is None

        rv = self.sign_in('', 'q')
        assert not rv['success']
        assert 'Wrong username or password.' in rv['message']
        assert rv['data'] is None

        # Invalid sign in: bad password
        rv = self.sign_in('me@haeger.me', 'a')
        assert not rv['success']
        assert 'Wrong username or password.' in rv['message']
        assert rv['data'] is None

        # Invalid sign in: bad email
        rv = self.sign_in('woot@haeger.me', 'q')
        assert not rv['success']
        assert 'Wrong username or password.' in rv['message']
        assert rv['data'] is None

        # Valid sign in
        rv = self.sign_in('me@haeger.me', 'q')
        assert rv['success']
        assert 'Successfully signed in.' in rv['message']
        assert rv['data'] is not None

        # TODO Write better test of tokens
        # Valid sign ins, is token ever the same?
        # Could fail, is it doesn't save more than one token..
        # token = []
        # bunch_of_times = 50
        # for x in range(0, bunch_of_times):
        #     rv = self.sign_in('me@haeger.me', 'q')
        #     assert rv['success']
        #     assert 'Successfully signed in.' in rv['message']
        #     assert rv['data'] is not None
        #     token.append(rv['data'])
        #
        # for x in range(0, bunch_of_times):
        #     for y in range(0, bunch_of_times):
        #         if x != y:
        #             assert token[x] != token[y]

    def test_sign_up(self):
        # Invalid sign up: Missing all data
        rv = self.sign_up('', '', '', '', '', '', '')
        assert not rv['success']
        assert 'Form data not complete' in rv['message']

        # Invalid sign up: Missing some data
        rv = self.sign_up('', 'Hager', 'Linkoping', 'Sweden', 'Male', 'blah@haeger.me', 'q')
        assert not rv['success']
        assert 'Form data not complete' in rv['message']

        rv = self.sign_up('Alexander', '', 'Linkoping', 'Sweden', 'Male', 'blah@haeger.me', 'q')
        assert not rv['success']
        assert 'Form data not complete' in rv['message']

        rv = self.sign_up('Alexander', 'Hager', '', 'Sweden', 'Male', 'me@haeger.me', 'q')
        assert not rv['success']
        assert 'Form data not complete' in rv['message']

        rv = self.sign_up('Alexander', 'Hager', 'Linkoping', '', 'Male', 'blah@haeger.me', 'q')
        assert not rv['success']
        assert 'Form data not complete' in rv['message']

        rv = self.sign_up('Alexander', 'Hager', 'Linkoping', 'Sweden', '', 'blah@haeger.me', 'q')
        assert not rv['success']
        assert 'Form data not complete' in rv['message']

        rv = self.sign_up('Alexander', 'Hager', 'Linkoping', 'Sweden', 'Male', '', 'q')
        assert not rv['success']
        assert 'Form data not complete' in rv['message']

        rv = self.sign_up('Alexander', 'Hager', 'Linkoping', 'Sweden', 'Male', 'blah@haeger.me', '')
        assert not rv['success']
        assert 'Form data not complete' in rv['message']

        # Invalid sign up: User already exist
        rv = self.sign_up('Alexander', 'Hager', 'Linkoping', 'Sweden', 'Male', 'me@haeger.me', 'q')
        assert not rv['success']
        assert 'User already exist' in rv['message']

        # Valid sign up
        rv = self.sign_up('Jane', 'Doe', 'New York', 'USA', 'Female', 'doe@example.com', 'a')
        assert rv['success']
        assert 'Successfully created a new user' in rv['message']

        # Invalid sign up: This user just signed up
        rv = self.sign_up('Jane', 'Doe', 'New York', 'USA', 'Female', 'doe@example.com', 'a')
        assert not rv['success']
        assert 'User already exists' in rv['message']

    def test_sign_out(self):
        # Valid sign out
        # Not the best way to test this though...
        sign_in_data = self.sign_in('me@haeger.me', 'q')
        assert sign_in_data['success']  # Not main test, but should work
        rv = self.sign_out(sign_in_data['data'])
        assert rv['success']
        assert "Successfully signed out" in rv['message']

        # Invalid sign out: sign out same user again
        rv = self.sign_out(sign_in_data['data'])
        assert not rv['success']
        assert "You are not signed in" in rv['message']

        # Invalid sign out: bad tokens
        rv = self.sign_out('')
        assert not rv['success']
        assert "You are not signed in" in rv['message']

        rv = self.sign_out('bleh')
        assert not rv['success']
        assert "You are not signed in" in rv['message']

    def test_change_password(self):
        # Get token
        data = self.sign_in('me@haeger.me', 'q')
        assert data['success']
        token = data['data']

        # Invalid change: bad token
        rv = self.change_password("meh", 'q', 'a')
        assert not rv['success']
        assert "You are not logged in" in rv['message']

        # Invalid change: bad old_password
        rv = self.change_password(token, '', 'a')
        assert not rv['success']
        assert "Wrong password" in rv['message']

        # Invalid change: bad new_password
        rv = self.change_password(token, 'q', '')
        assert not rv['success']
        assert "New password sucks" in rv['message']

        # Valid change
        rv = self.change_password(token, 'q', 'a')
        assert rv['success']
        assert "Password changed" in rv['message']

        # Did password change stick? This should fail now.
        rv = self.change_password(token, 'q', 'a')
        assert not rv['success']
        assert "Wrong password" in rv['message']

    def test_get_user_data_by_email(self):
        # Get token
        data = self.sign_in('me@haeger.me', 'q')
        assert data['success']
        token = data['data']

        # Bad token
        rv = self.get_user_data_by_email('', 'me@haeger.me')
        assert not rv['success']
        assert "You are not signed in" in rv['message']
        assert rv['data'] is None

        # Bad email
        rv = self.get_user_data_by_email(token, '')
        assert not rv['success']
        assert "No such user" in rv['message']
        assert rv['data'] is None

        # Valid token
        rv = self.get_user_data_by_email(token, 'me@haeger.me')
        assert rv['success']
        assert "User data retrieved" in rv['message']
        assert rv['data']['firstname'] == 'Alexander'
        assert rv['data']['lastname'] == 'Haeger'
        assert rv['data']['city'] == 'Linkoping'
        assert rv['data']['country'] == 'Sweden'
        assert rv['data']['gender'] == 'Male'
        assert rv['data']['email'] == 'me@haeger.me'

    def test_get_user_data_by_token(self):
        # Implemented with the same function as get_user_data_by_email(),
        # so no extensive tests here

        # Get token
        data = self.sign_in('me@haeger.me', 'q')
        assert data['success']
        token = data['data']

        # Invalid token
        rv = self.get_user_data_by_token("Meh")
        assert not rv['success']

        # Valid token
        rv = self.get_user_data_by_token(token)
        assert rv['success']

    def test_post_message(self):
        # Get token
        data = self.sign_in('me@haeger.me', 'q')
        assert data['success']
        token = data['data']

        # Bad token
        rv = self.post_message('', "What's up?", 'me@haeger.me')
        assert not rv['success']
        assert "You are not signed in" in rv['message']

        # Bad email
        rv = self.post_message(token, "What's up?", 'meh')
        assert not rv['success']
        assert "No such user" in rv['message']

        # Valid posts
        rv = self.post_message(token, "What's up?", 'me@haeger.me')
        assert rv['success']
        assert "Message posted" in rv['message']

        rv = self.post_message(token, "", 'me@haeger.me')
        assert rv['success']
        assert "Message posted" in rv['message']

        # Get a new user and post successfully
        rv = self.sign_up('Jane', 'Doe', 'New York', 'USA', 'Female', 'doe@example.com', 'a')
        assert rv['success']
        new_user = self.sign_in('doe@example.com', 'a')
        assert new_user['success']
        rv = self.post_message(token, 'Whaddap?', 'doe@example.com')
        assert rv['success']
        assert "Message posted" in rv['message']

    def test_get_user_messages_by_email(self):
        # Get token
        data = self.sign_in('me@haeger.me', 'q')
        assert data['success']
        token = data['data']

        # Bad token
        rv = self.get_user_messages_by_email('', 'me@haeger.me')
        assert not rv['success']
        assert 'You are not signed in' in rv['message']
        assert rv['data'] is None

        # Bad email
        rv = self.get_user_messages_by_email(token, '')
        assert not rv['success']
        assert 'No such user' in rv['message']
        assert rv['data'] is None

        # Valid
        rv = self.get_user_messages_by_email(token, 'me@haeger.me')
        assert rv['success']
        assert 'User messages retrieved' in rv['message']
        assert rv['data'] is not None

        # Post a message so something can be retrieved
        rv = self.post_message(token, 'Hey me!', 'me@haeger.me')
        assert rv['success']
        rv = self.post_message(token, 'Whaddup?', 'me@haeger.me')
        assert rv['success']
        rv = self.get_user_messages_by_email(token, 'me@haeger.me')
        assert rv['success']
        assert 'User messages retrieved' in rv['message']
        assert rv['data'][0]['writer'] == 'me@haeger.me'
        assert rv['data'][0]['content'] == 'Whaddup?'
        assert rv['data'][1]['writer'] == 'me@haeger.me'
        assert rv['data'][1]['content'] == 'Hey me!'

    def test_get_user_messages_by_token(self):
        # Based on the same methods as get_user_data_by_email,
        # so no thorough testing here

        # Get token
        data = self.sign_in('me@haeger.me', 'q')
        assert data['success']
        token = data['data']

        # Bad token
        rv = self.get_user_data_by_token('')
        assert not rv['success']

        # Valid
        rv = self.get_user_data_by_token(token)
        assert rv['success']

    def test_final_test(self):
        rv = self.sign_up('John', 'Doe', 'New York', 'USA', 'Male', 'john@example.com', 'q')
        assert rv['success']
        rv = self.sign_up('Jane', 'Doe', 'New York', 'USA', 'Female', 'jane@example.com', 'a')
        assert rv['success']
        rv = self.sign_in('john@example.com', 'q')
        assert rv['success']
        token = rv['data']
        rv = self.post_message(token, 'Hey Jane!', 'jane@example.com')
        assert rv['success']
        rv = self.get_user_messages_by_email(token, 'jane@example.com')
        assert rv['success']
        assert rv['data'][0]['writer'] == 'john@example.com'
        assert rv['data'][0]['content'] == 'Hey Jane!'
        rv = self.sign_out(token)
        assert rv['success']
        rv = self.sign_in('jane@example.com', 'a')
        assert rv['success']
        token = rv['data']
        rv = self.post_message(token, 'Hey me!', 'jane@example.com')
        assert rv['success']
        rv = self.get_user_messages_by_token(token)
        assert rv['success']
        assert rv['data'][0]['writer'] == 'jane@example.com'
        assert rv['data'][0]['content'] == 'Hey me!'
        rv = self.sign_out(token)
        assert rv['success']

    def sign_up(self, firstname, lastname, city, country, gender, email, password):
        return json.loads(self.app.post('/sign_up', data=dict(firstname=firstname, lastname=lastname, city=city,
                                                              country=country, gender=gender, email=email,
                                                              password=password)).data)

    def sign_in(self, email, password):
        return json.loads(self.app.post('/sign_in', data=dict(email=email, password=password)).data)

    def sign_out(self, token):
        return json.loads(self.app.post('/sign_out', data=dict(token=token)).data)

    def change_password(self, token, old_password, new_password):
        return json.loads(self.app.post('/change_password', data=dict(token=token, old_password=old_password,
                                                                      new_password=new_password)).data)

    def get_user_data_by_token(self, token):
        return json.loads(self.app.post('/get_user_data_by_token', data=dict(token=token)).data)

    def get_user_data_by_email(self, token, email):
        return json.loads(self.app.post('/get_user_data_by_email', data=dict(token=token, email=email)).data)

    def post_message(self, token, message, email):
        return json.loads(self.app.post('/post_message', data=dict(token=token, message=message,
                                                                   email=email)).data)

    def get_user_messages_by_email(self, token, email):
        return json.loads(self.app.post('/get_user_messages_by_email', data=dict(token=token, email=email)).data)

    def get_user_messages_by_token(self, token):
        return json.loads(self.app.post('/get_user_messages_by_token', data=dict(token=token)).data)

if __name__ == '__main__':
    unittest.main()