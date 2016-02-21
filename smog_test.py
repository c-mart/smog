import unittest
import smog
import smog.models
from datetime import datetime
import re


class smogTestCase(unittest.TestCase):

    test_user_email = 'test@test.com'
    test_user_password = 'changeme123'

    def setUp(self):
        smog.app.config.from_object('smog.config_test')
        self.app = smog.app.test_client()
        smog.init_db()

    def tearDown(self):
        smog.db.session.remove()
        smog.db.drop_all()

    def login(self, email, password):
        return self.app.post('/login', data=dict(email=email, password=password), follow_redirects=True)

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)

    def test_no_posts(self):
        r = self.app.get('/')
        assert 'No posts yet.' in r.data, "We should see no posts"

    def test_login_logout(self):
        r = self.login('invalid', 'credentials')
        assert 'Invalid email or password, try again.' in r.data, "We should receive an invalid credentials message"
        r = self.login(self.test_user_email, self.test_user_password)
        assert 'You are logged in.' in r.data, "We should receive a logged in notice"
        r = self.logout()
        assert 'You are logged out.' in r.data, "We should receive a logged out notice"

    def test_logged_out_cannot_create(self):
        r = self.app.get('/create', follow_redirects=True)
        assert 'Please log in to access this page.' in r.data, "We should see a notice asking to log in"

    def test_rate_limit_login(self):
        smog.app.config['RATELIMIT_ENABLED'] = True
        assert False

    def test_compose_post(self):
        self.login(self.test_user_email, self.test_user_password)
        r = self.app.get('/create')
        assert '<h1>Create Post</h1>' in r.data

    def test_create_post(self):
        self.login(self.test_user_email, self.test_user_password)
        r = self.app.post('/create', data=dict(
            title='Test post',
            body='The quick brown fox jumps over the lazy dog',
            description='Test description',
            permalink='test-permalink',
            published=True,
            comments_allowed=True
        ), follow_redirects=True)
        assert 'The quick brown fox jumps over the lazy dog' in r.data, "We should see post body"
        assert 'Posted by Test User' in r.data, "We should see name of user posting"
        assert 'on ' + datetime.utcnow().strftime('%Y-%m-%d') in r.data, "We should see creation date"

    def test_auto_permalink(self):
        self.login(self.test_user_email, self.test_user_password)
        r = self.app.post('/create', data=dict(
            title='Test post',
            body='The quick brown fox jumps over the lazy dog',
            description='',
            permalink='',
            published=True,
            comments_allowed=True
        ), follow_redirects=True)
        assert '<a href="/posts/test-post">' in r.data, "We should see automatically generated permalink"

    def test_follow_permalink(self):
        self.login(self.test_user_email, self.test_user_password)
        r = self.app.post('/create', data=dict(
            title='Test post',
            body='The quick brown fox jumps over the lazy dog',
            description='Test description',
            permalink='test-permalink',
            published=True,
            comments_allowed=True
        ), follow_redirects=True)
        assert '<a href="/posts/test-permalink">' in r.data, "We should see link for post permalink"
        # Following permalink
        r = self.app.get('/posts/test-permalink')
        assert 'The quick brown fox jumps over the lazy dog' in r.data, "We should see post body"

    def test_edit_post(self):
        self.login(self.test_user_email, self.test_user_password)
        r = self.app.post('/create', data=dict(
            title='Test post',
            body='The quick brown fox jumps over the lazy dog',
            description='Test description',
            permalink='test-permalink',
            published=True,
            comments_allowed=True
        ), follow_redirects=True)
        post_id = re.search("/create\?id=([0-9]+)", r.data).group(1)
        r = self.app.get('/create?id=' + str(post_id))
        assert '<h1>Edit Post</h1>' in r.data, "We should see edit page"
        r = self.app.post('/create', data=dict(
            update_id=post_id,
            title='Test post',
            body='The quack bruno fax stumps the lousy doug',
            description='Test description',
            permalink='test-permalink',
            published=True,
            comments_allowed=True
        ), follow_redirects=True)

        assert 'The quack bruno fax stumps the lousy doug' in r.data, "We should see edited post body"
        assert 'The quick brown fox jumps over the lazy dog' not in r.data, "We should see edited post body"

    def test_create_unpublished_post_then_publish(self):
        self.login(self.test_user_email, self.test_user_password)
        r = self.app.post('/create', data=dict(
            title='Test post',
            body='The quick brown fox jumps over the lazy dog',
            description='Test description',
            permalink='test-permalink',
            comments_allowed=True
        ), follow_redirects=True)
        assert 'No posts yet.' in r.data, "We should see no published posts"
        r = self.app.get('/unpublished')
        assert 'The quick brown fox jumps over the lazy dog' in r.data, "We should see post in /unpublished"

    def test_delete_post(self):
        self.login(self.test_user_email, self.test_user_password)
        r = self.app.post('/create', data=dict(
            title='Test post',
            body='The quick brown fox jumps over the lazy dog',
            description='Test description',
            permalink='test-permalink',
            published=True,
            comments_allowed=True
        ), follow_redirects=True)
        post_id = re.search("/create\?id=([0-9]+)", r.data).group(1)
        r = self.app.get('/create?id=' + str(post_id))
        assert re.search("<a href=\"/delete/[0-9]+\">Delete post</a>", r.data) is not None, "Delete link is missing"
        r = self.app.get('/delete/' + str(post_id), follow_redirects=True)
        assert "Post has been deleted." in r.data, "User should receive notice that post has been deleted"
        assert "No posts yet." in r.data, "We should see no posts now"

    def test_cannot_create_duplicate_post(self):
        # Try to create two identical posts, we should not be able to
        self.login(self.test_user_email, self.test_user_password)
        self.app.post('/create', data=dict(
            title='Test post',
            body='The quick brown fox jumps over the lazy dog',
            description='Test description',
            permalink='test-permalink',
            published=True,
            comments_allowed=True
        ), follow_redirects=True)
        r = self.app.post('/create', data=dict(
            title='Test post',
            body='The quick brown fox jumps over the lazy dog',
            description='Test description',
            permalink='test-permalink',
            published=True,
            comments_allowed=True
        ), follow_redirects=True)
        assert 'There was a problem creating your post.' in r.data, "User should receive error message"
        r = self.app.get('/')
        assert r.data.count("<h2><a href=\"/posts/test-permalink\">Test post</a></h2>") == 1,\
            "Duplicate posts exist where they should not"

    def test_markdown_parsing(self):
        self.login(self.test_user_email, self.test_user_password)
        r = self.app.post('/create', data=dict(
            title='Test post',
            # Test Markdown input
            body='### Heading\n'
                 '- Bullet\n\n'
                 'Paragraph\n\n'
                 '    some_code()',
            description='Test description',
            permalink='test-permalink',
            published=True,
            comments_allowed=True
        ), follow_redirects=True)
        assert all(x in r.data for x in
                   ['<h3>Heading</h3>', '<li>Bullet</li>', '<p>Paragraph</p>', '<code>some_code()\n</code>']
                   ), "Markdown not parsed correctly"


if __name__ == '__main__':
    unittest.main()
