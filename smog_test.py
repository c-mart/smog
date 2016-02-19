import unittest
from smog import *
from datetime import datetime

# TODO test posting with special characters in title and no permalink field


class smogTestCase(unittest.TestCase):
    test_user_email = 'test@test.com'
    test_user_password = 'changeme123'

    def setUp(self):
        app.config['DB_PATH'] = "sqlite:////tmp/smog-test.sqlite"
        app.config['TESTING'] = True
        self.app = app.test_client()
        db.create_all()
        # todo should I be testing for the User class rather than assuming it will work?
        testuser = User(self.test_user_email, 'Test User', self.test_user_password)
        db.session.add(testuser)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def login(self, email, password):
        return self.app.post('/login', data=dict(email=email, password=password), follow_redirects=True)

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)

    def test_login_logout(self):
        r = self.login('invalid', 'credentials')
        assert 'Invalid email or password, try again.' in r.data
        r = self.login(self.test_user_email, self.test_user_password)
        assert 'You are logged in.' in r.data
        r = self.logout()
        assert 'You are logged out.' in r.data

    def test_logged_out_cannot_create(self):
        r = self.app.get('/create', follow_redirects=True)
        assert 'Please log in to access this page.' in r.data

    def test_create_post(self):
        self.login(self.test_user_email, self.test_user_password)
        r = self.app.post('/create', data=dict(
            title='Test post',
            body='The quick brown fox jumps over the lazy dog',
            description='Test description',
            permalink='test-permalink',
            published='True',
            comments_allowed='True',
        ), follow_redirects=True)
        assert 'The quick brown fox jumps over the lazy dog' in r.data
        assert 'posted on ' + datetime.utcnow().strftime('%Y-%m-%d') in r.data

    def test_create_draft(self):
        assert False

    def test_edit_post(self):
        assert False

    def test_delete_post(self):
        assert False

    def test_cannot_create_duplicate_post(self):
        assert False

if __name__ == '__main__':
    unittest.main()
