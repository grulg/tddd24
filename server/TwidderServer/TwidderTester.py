__author__ = 'haeger'
import os
import twidder
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

    def test_hello_world(self):
        rv = self.app.get('/')
        assert 'Hello World!' in rv.data

    # Sending any parameter as 'None' will result in
    # HTTP error code 400 'Bad Request', and is therefore
    # not tested

    # TODO Need to check token
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

        # Valid sign ins, is token ever the same?
        token = []
        for x in range(0, 100):
            rv = self.sign_in('me@haeger.me', 'q')
            assert rv['success']
            assert 'Successfully signed in.' in rv['message']
            assert rv['data'] is not None
            token.append(rv['data'])

        for x in range(0, 100):
            for y in range(0, 100):
                if x != y:
                    assert token[x] != token[y]

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

    def sign_up(self, firstname, lastname, city, country, gender, email, password):
        return json.loads(self.app.post('/sign_up', data=dict(firstname=firstname, lastname=lastname, city=city,
                                                              country=country, gender=gender, email=email,
                                                              password=password)).data)

    def sign_in(self, email, password):
        return json.loads(self.app.post('/sign_in', data=dict(email=email, password=password)).data)

if __name__ == '__main__':
    unittest.main()