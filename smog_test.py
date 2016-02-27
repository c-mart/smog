import unittest
import smog
import smog.models
from datetime import datetime
import re


class smogTestCase(unittest.TestCase):

    test_user_email = 'test@test.com'
    test_user_password = 'changeme123'

    def setUp(self):
        """Set up each test: initialize test client and database, disable rate limiter."""
        smog.app.config.from_object('smog.config_test')
        self.app = smog.app.test_client()
        smog.init_db()
        smog.limiter.enabled = False

    def tearDown(self):
        """Empty the database as cleanup after each test"""
        smog.db.session.remove()
        smog.db.drop_all()

    # Helper Methods
    def login(self, email=test_user_email, password=test_user_password):
        """Logs test user in."""
        return self.app.post('/login', data=dict(email=email, password=password), follow_redirects=True)

    def logout(self):
        """Logs test user out."""
        return self.app.get('/logout', follow_redirects=True)

    def create_post(self,
                    title='Test post',
                    body='The quick brown fox jumps over the lazy dog',
                    description='Test description',
                    permalink='',
                    static_page=False,
                    published=True,
                    comments_allowed=True):
        """Creates test post."""
        return self.app.post('/create', data=locals(), follow_redirects=True)

    # Test Cases
    def test_no_posts(self):
        """Confirm lack of posts with new database"""
        r = self.app.get('/')
        assert 'No posts yet.' in r.data, "We should see no posts"

    def test_login_logout(self):
        """Perform invalid login attempt, log user in, log user out"""
        r = self.login('invalid', 'credentials')
        assert 'Invalid email or password, try again.' in r.data, "We should receive an invalid credentials message"
        r = self.login()
        assert 'You are logged in.' in r.data, "We should receive a logged in notice"
        r = self.logout()
        assert 'You are logged out.' in r.data, "We should receive a logged out notice"

    def test_logged_out_cannot_create(self):
        """Confirm that we cannot access the New Post page, or create a new post, while logged out"""
        r = self.app.get('/create', follow_redirects=True)
        assert 'Please log in to access this page.' in r.data, "We should see a notice asking to log in"
        r = self.create_post()
        assert 'Please log in to access this page.' in r.data, "We should see a notice asking to log in"

    def test_rate_limit_login(self):
        """Try logging in with invalid credentials too many times, confirm that the rate limiter kicks in"""
        smog.limiter.enabled = True
        for x in range(6):
            self.login('invalid', 'credentials')
        r = self.login('invalid', 'credentials')
        assert 'You have tried doing that too often' in r.data, "We should see a rate limit warning."
        r = self.login(self.test_user_email, self.test_user_password)
        assert 'logged in' not in r.data, 'Rate limiter should not allow us to log in'
        assert 'You have tried doing that too often' in r.data, "We should see a rate limit warning."

    def test_compose_post(self):
        """Access the Create Post page."""
        self.login()
        r = self.app.get('/create')
        assert '<h2>Create Post</h2>' in r.data

    def test_create_post(self):
        """Create a post and confirm that we can see it."""
        self.login()
        r = self.create_post()
        assert 'The quick brown fox jumps over the lazy dog' in r.data, "We should see post body"
        assert 'Posted by Test User' in r.data, "We should see name of user posting"
        assert 'on ' + datetime.utcnow().strftime('%Y-%m-%d') in r.data, "We should see creation date"

    def test_auto_permalink(self):
        """Confirm automatic generation of permalink with new post."""
        self.login()
        r = self.create_post()
        assert '<a href="/posts/test-post">' in r.data, "We should see automatically generated permalink"

    def test_follow_permalink(self):
        """Confirm that a permalink works as expected."""
        self.login()
        r = self.create_post()
        assert '<a href="/posts/test-post">' in r.data, "We should see link for post permalink"
        # Following permalink
        r = self.app.get('/posts/test-post')
        assert 'The quick brown fox jumps over the lazy dog' in r.data, "We should see post body"

    def test_cannot_access_permalink_unpublished(self):
        """Confirm that we cannot see an unpublished post by its permalink while not logged in."""
        self.login()
        self.create_post(published=False)
        # Following permalink
        r = self.app.get('/posts/test-post')
        assert 'The quick brown fox jumps over the lazy dog' in r.data,\
            "Unpublished post should load while we are logged in"
        self.logout()
        r = self.app.get('/posts/test-post')
        assert r.status_code == 404, "Trying to access unpublished post while not logged in should get us a 404"

    def test_clean_up_permalink(self):
        """Confirm that if a user enters a stupid permalink, it is cleaned up by slugify."""
        self.login()
        self.create_post(permalink="This: is An ugly/dirty permalink --")
        r = self.app.get('/posts/this-is-an-ugly-dirty-permalink')
        assert 'The quick brown fox jumps over the lazy dog' in r.data, "Permalink was not sanitized"

    def test_description_single_post(self):
        """Confirm that the post description is properly set in the meta tag when viewing a single post page"""
        self.login()
        self.create_post()
        r = self.app.get('/posts/test-post')
        assert '<meta name="description" content="Test description" />' in r.data,\
            "We should see our post description in a meta tag on the single-post page"

    def test_edit_post(self):
        """Confirm that we can edit basically every element of a post and see the results."""
        self.login()
        r = self.create_post()
        post_id = re.search("/create\?id=([0-9]+)", r.data).group(1)
        r = self.app.get('/create?id=' + str(post_id))
        assert '<h2>Edit Post</h2>' in r.data, "We should see edit page"
        assert 'The quick brown fox jumps over the lazy dog' in r.data, "We should see our post body in the edit page"
        r = self.app.post('/create', data=dict(
            update_id=post_id,
            title='Test post',
            body='The quack bruno fax stumps the lousy doug',
            description='Test description',
            permalink='test-post',
            static_page=False,
            published=True,
            comments_allowed=True
        ), follow_redirects=True)

        assert 'The quack bruno fax stumps the lousy doug' in r.data, "We should see edited post body"
        assert 'The quick brown fox jumps over the lazy dog' not in r.data, "We should see edited post body"

    def test_create_unpublished_post_then_publish(self):
        """Confirm we can create an unpublished post and it shows up in the right place, then publish it and check
        again.
        """
        self.login()
        r = self.create_post(published=False)
        assert 'No posts yet.' in r.data, "We should see no published posts"
        r = self.app.get('/unpublished')
        assert 'The quick brown fox jumps over the lazy dog' in r.data, "We should see post in /unpublished"
        post_id = re.search("/create\?id=([0-9]+)", r.data).group(1)
        self.app.post('/create', data=dict(
            update_id=post_id,
            title='Test post',
            body='The quick brown fox jumps over the lazy dog',
            description='',
            permalink='',
            static_page=False,
            published=True,
            comments_allowed=True
        ), follow_redirects=True)
        r = self.app.get('/')
        assert 'The quick brown fox jumps over the lazy dog' in r.data, "We should see the now-published post on the home page"

    def test_delete_post(self):
        """Create a post and then delete it"""
        self.login()
        r = self.create_post()
        post_id = re.search("/create\?id=([0-9]+)", r.data).group(1)
        r = self.app.get('/create?id=' + str(post_id))
        assert re.search("<a href=\"/delete/[0-9]+\">Delete post</a>", r.data) is not None, "Delete link is missing"
        r = self.app.get('/delete/' + str(post_id), follow_redirects=True)
        assert "Post has been deleted." in r.data, "User should receive notice that post has been deleted"
        assert "No posts yet." in r.data, "We should see no posts now"

    def test_cannot_create_duplicate_post(self):
        """Try to create two identical posts, we should not be able to"""
        self.login()
        self.create_post()
        r = self.create_post()
        assert 'There was a problem creating your post.' in r.data, "User should receive error message"
        r = self.app.get('/')
        assert r.data.count("<h2 class=\"post-title\"><a href=\"/posts/test-post\">Test post</a></h2>") == 1,\
            "Duplicate posts exist where they should not"

    def test_markdown_parsing(self):
        """Confirm that markdown syntax in a post body is automatically parsed as HTML for display."""
        self.login()
        r = self.create_post(body='### Heading\n'
                             '- Bullet\n\n'
                             'Paragraph\n\n'
                             '    some_code()',)
        assert all(x in r.data for x in
                   ['<h3>Heading</h3>', '<li>Bullet</li>', '<p>Paragraph</p>', '<code>some_code()\n</code>']
                   ), "Markdown not parsed correctly"

    def test_post_static_page(self):
        """Create a static page, confirm it shows up in the nav bar and we can load it."""
        self.login()
        self.create_post(static_page=True)
        r = self.app.get('/')
        assert 'No posts yet.' in r.data, "We should see no posts"
        assert '<span class="nav-item"><a href="/posts/test-post">Test post</a></span>' in r.data,\
            "We should see a link to our static page in the navigation"
        r = self.app.get('/posts/test-post')
        assert "The quick brown fox jumps over the lazy dog" in r.data, "We should see our static page"

    def test_list_posts(self):
        """Confirm that the All Posts page displays a list of posts."""
        self.login()
        self.create_post(title='post 1')
        self.create_post(title='post 2')
        r = self.app.get('/list')
        assert '<a href="/posts/post-1">post 1</a>' in r.data and \
               '<a href="/posts/post-2">post 2</a>' in r.data, \
               'We should see a list of posts a link to our test post'

    def test_atom_feed(self):
        """Confirm that posts show up in the Atom feed."""
        self.login()
        self.create_post()
        self.create_post(title="Can't C Me", body="The blind stares of a million pairs of eyes", published=False)
        r = self.app.get('/')
        assert '<link href="/posts.atom" rel="alternate" title="Recent Posts" type="application/atom+xml">' in r.data,\
            "We should see a link to an Atom feed"
        r = self.app.get('/list')
        assert '<link href="/posts.atom" rel="alternate" title="Recent Posts" type="application/atom+xml">' in r.data,\
            "We should see a link to an Atom feed"
        r = self.app.get('/posts.atom')
        assert '<feed xmlns="http://www.w3.org/2005/Atom">' in r.data, "An Atom feed should load"
        assert 'The quick brown fox jumps over the lazy dog' in r.data, "We should see our post in the Atom feed"
        assert "Can't C me" not in r.data, "We should not see unpublished posts in the Atom feed"

    def test_settings(self):
        """Confirm that site settings are passed to templates, we can update the settings, and changes propagate."""
        self.login()
        r = self.app.get('/site-settings')
        assert 'Site Settings' in r.data and '<form' in r.data, 'A site settings page should load'
        self.app.post('/site-settings',
                      data=dict(site_title='dis b mah blog', footer_line='dis b mah foot'),
                      follow_redirects=True)
        r = self.app.get('/')
        assert '<title>dis b mah blog</title>' in r.data, 'We should see the title that we just set'
        assert '<div class="footer">dis b mah foot</div>' in r.data, 'We should see the footer line that we just set'

    def test_title_shows_post_title(self):
        """Confirm that the HTML title shows the post title if we load a single-post page"""
        self.login()
        self.create_post()
        r = self.app.get('/posts/test-post')
        print(r.data)
        assert '<title>Test post - smog: Simple Markdown blOG</title>' in r.data,\
            "We should see the post title in HTML <title> tag if we load a single-post page"

if __name__ == '__main__':
    unittest.main()