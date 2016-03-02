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
                    static_page_link_title='',
                    published=True,
                    comments_allowed=True):
        """Creates test post."""
        return self.app.post('/create', data=locals(), follow_redirects=True)

    def create_user(self,
                    name='Milton Waddams',
                    email='milton@waddams.com',
                    password='creosote',
                    active=True):
        """Creates a user account."""
        return self.app.post('/create-edit-user', data=locals(), follow_redirects=True)

    # Test Cases
    def test_no_posts(self):
        """Confirm lack of posts with new database"""
        r = self.app.get('/')
        assert 'No posts yet.' in r.data, "We should see no posts"

    # Test Cases - Authentication
    def test_login_logout(self):
        """Perform invalid login attempt, log user in, log user out"""
        r = self.login('invalid', 'credentials')
        assert 'No active account associated with that email and password, try again.' in r.data,\
            "We should receive an invalid credentials message"
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

    # Test Cases - CRUDing posts
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

    def test_title_shows_post_title(self):
        """Confirm that the HTML title shows the post title if we load a single-post page"""
        self.login()
        self.create_post()
        r = self.app.get('/posts/test-post')
        assert '<title>Test post - smog: Simple Markdown blOG</title>' in r.data,\
            "We should see the post title in HTML <title> tag if we load a single-post page"

    def test_list_posts(self):
        """Confirm that the All Posts page displays a list of posts."""
        self.login()
        self.create_post(title='post 1')
        self.create_post(title='post 2')
        r = self.app.get('/list')
        assert '<a href="/posts/post-1">post 1</a>' in r.data and \
               '<a href="/posts/post-2">post 2</a>' in r.data, \
               'We should see a list of posts a link to our test post'

    # Test Cases - Syndication
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

    def test_only_recent_in_atom_feed(self):
        """Create many posts and confirm that the atom feed only shows the most recent."""
        self.login()
        for i in range(30):
            self.create_post(title='post ' + str(i))
        r = self.app.get('/posts.atom')
        assert '<feed xmlns="http://www.w3.org/2005/Atom">' in r.data, "An Atom feed should load"
        assert '<title type="text">post 29</title>' in r.data, "We should see our most recent post in the Atom feed"
        assert '<title type="text">post 19</title>' in r.data, "We should see a post 10 posts old in the Atom feed"
        assert '<title type="text">post 5</title>' not in r.data, "We should not see a very old post in the Atom feed"

    # Test Cases - User Input Parsing
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

    # Test Cases - Static Pages
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

    def test_static_page_in_timeline(self):
        """Toggle static_page_in_timeline, and confirm that a static page either displays in timeline or not"""
        self.login()
        self.create_post(title='Test static page', static_page=True)
        r = self.app.get('/')
        assert 'No posts yet' in r.data, 'We should not see our static page in the timeline'
        r = self.app.get('/posts/test-static-page')
        assert 'The quick brown fox jumps over the lazy dog' in r.data,\
            'We should see our static page when we load the permalink'
        post_id = re.search("/create\?id=([0-9]+)", r.data).group(1)
        r = self.app.post('/create', data=dict(
            update_id=post_id,
            title='Test static page',
            body='The quick brown fox jumps over the lazy dog',
            description='Test description',
            permalink='test-static-page',
            static_page=True,
            static_page_link_title='Test static page',
            static_page_in_timeline=True,
            published=True,
            comments_allowed=True
        ), follow_redirects=True)
        r = self.app.get('/')
        assert '<a href="/posts/test-static-page">Test static page</a>' in r.data,\
            "We should see the link to our static page in the site menu"
        assert 'The quick brown fox jumps over the lazy dog' in r.data,\
            'We should see the body of our static page in the timeline'

    def test_static_page_link_title(self):
        """Confirm that we can set a custom static page link title and it's displayed in the site menu"""
        self.login()
        self.create_post(title='Test static page', static_page=True, static_page_link_title='spegy and merbls')
        r = self.app.get('/')
        assert '<a href="/posts/test-static-page">spegy and merbls</a>' in r.data,\
            "We should see our custom link title in the site menu"

    # Test Cases - User Management
    def test_crud_users(self):
        """Create, modify, and delete user accounts.

        This is more of an "integration test" than a unit test, which proves the entire user management workflow.
        Here is what we do:
        - Log in as Test User
        - Create account for Rumpel Stiltskin
        - Log out and log in as Rumpel Stiltskin
        - Load "Manage Users" page and obtain edit user link for Test User
        - Load "Edit User" page for Test User
        - Rename Test User to Bob Loblaw, also change email and password
        - Log out and log in as Bob Loblaw
        - Delete Rumpel Stiltskin
        - Log out and try logging in as Rumpel Stiltskin, we shouldn't be able to
        """
        # Log in as Test User
        self.login()
        # Create account for Rumpel Stiltskin
        r = self.app.post('/create-edit-user', data=dict(
            name='Rumpel Stiltskin',
            email='rumpel@stilt.skin',
            password='cheesefries99',
            active=True
        ), follow_redirects=True)
        assert 'User Rumpel Stiltskin has been saved.' in r.data, 'User account saved message should appear'
        assert '<td>Rumpel Stiltskin</td>' in r.data, 'User name should appear on manage users page'
        assert '<td>rumpel@stilt.skin</td>' in r.data, 'User email should appear on manage users page'
        assert '<td>Active</td>' in r.data, 'User enabled status should appear on manage users page'
        # Log out and log in as Rumpel Stiltskin
        self.logout()
        r = self.login(email='rumpel@stilt.skin', password='cheesefries99')
        assert 'Logged in as Rumpel Stiltskin.' in r.data, 'Should be logged in as new user'
        # Load "Manage Users" page and obtain edit user link for Test User
        r = self.app.get('/manage-users')
        reg_exp = re.search(
            '<td>Test User<\/td>(.|\n)*?<td><a href="(\/create-edit-user\?id=([0-9]+))">', r.data)
        edit_link = reg_exp.group(2)
        edit_user_id = reg_exp.group(3)
        # Load "Edit User" page for Test User
        r = self.app.get(edit_link)
        assert '<h1>Edit User</h1>' in r.data and 'value="Test User"' in r.data, 'Edit user page should load'
        # Rename Test User to Bob Loblaw, also change email and password
        r = self.app.post('/create-edit-user', data=dict(
            update_id=edit_user_id,
            name='Bob Loblaw',
            email='bob@lob.law',
            password='chickenmeal',
            active=True
        ), follow_redirects=True)
        assert 'User Bob Loblaw has been saved.' in r.data, 'User account saved message should appear'
        assert '<td>Bob Loblaw</td>' in r.data, 'Updated user name should appear on manage users page'
        assert '<td>Test User</td>' not in r.data, 'Old user name should not appear on manage users page'
        assert '<td>bob@lob.law</td>' in r.data, 'Updated user email should appear on manage users page'
        assert '<td>test@test.com</td>' not in r.data, 'Old user email should not appear on manage users page'
        # Log out and log in as Bob Loblaw
        self.logout()
        r = self.login(email='bob@lob.law', password='chickenmeal')
        assert 'Logged in as Bob Loblaw' in r.data, 'Should be logged in as Bob Loblaw'
        # Delete Rumpel Stiltskin
        r = self.app.get('/manage-users')
        reg_exp = re.search(
            '<td>Rumpel Stiltskin<\/td>(.|\n)*?<td><a href="(\/create-edit-user\?id=([0-9]+))">', r.data)
        edit_link = reg_exp.group(2)
        delete_user_id = reg_exp.group(3)
        r = self.app.get(edit_link)
        assert '<a href="/delete-user/%s">' % delete_user_id in r.data, 'Should see a delete user link'
        r = self.app.get('/delete-user/' + str(delete_user_id), follow_redirects=True)
        assert 'User has been deleted.' in r.data, 'Should see notice that the user has been deleted.'
        assert 'Rumpel Stiltskin' not in r.data, 'Rumpel Stiltskin user should no longer display in manage users table'
        # Log out, try logging in as Rumpel Stiltskin, we shouldn't be able to
        self.logout()
        r = self.login(email='rumpel@stilt.skin', password='cheesefries99')
        assert 'No active account associated with that email and password, try again.' in r.data,\
            'We should not be able to log in as a deleted user'

    def test_delete_disable_own_account(self):
        """Confirm that we cannot disable or delete our own user account."""
        self.login()
        r = self.app.get('/manage-users')
        reg_exp = re.search(
            '<td>Test User<\/td>(.|\n)*?<td><a href="(\/create-edit-user\?id=([0-9]+))">', r.data)
        edit_user_id = reg_exp.group(3)
        r = self.app.post('/create-edit-user', data=dict(
            update_id=edit_user_id,
            name='Test User',
            email='test@test.com',
            password='',
            active=False
        ), follow_redirects=True)
        assert 'Error: you cannot disable your own user account.' in r.data,\
            'Should not be able to disable own account'
        self.logout()
        r = self.login()
        assert 'Logged in as Test User' in r.data, 'Our own account should not be disabled'

    def test_disabled_user_cannot_log_in(self):
        """Confirm that a disabled user cannot log in."""
        self.login()
        # Create disabled account
        r = self.app.post('/create-edit-user', data=dict(
            name='Jenkins Smith',
            email='jenkins@smith.com',
            password='pumpkin',
            active=False
        ), follow_redirects=True)
        assert 'User Jenkins Smith has been saved.' in r.data, 'User account saved message should appear'
        assert '<td>Jenkins Smith</td>' in r.data, 'User name should appear on manage users page'
        assert '<td>jenkins@smith.com</td>' in r.data, 'User email should appear on manage users page'
        assert '<td>Disabled</td>' in r.data, 'Account disabled status should appear on manage users page'
        # Log out and try to log in with disabled account
        self.logout()
        r = self.login(email='jenkins@smith.com', password='pumpkin')
        assert 'No active account associated with that email and password, try again.' in r.data,\
            'Should not be able to log in as disabled user'

    def test_disabled_logged_in_user_cannot_do_anything(self):
        """Confirm that as soon as we disable a user account, it is no longer able to do anything requiring login."""
        # TODO learn how to run two sessions side by side during a unit test, then update this code
        """
        r1 = self.login()
        # Create second account
        self.create_user()
        # Create second test_client() instance to log in as new user
        self.app2 = smog.app.test_client()
        self.app2.post('/login', data=dict(email='milton@waddams.com', password='creosote'), follow_redirects=True)
        # Disable new logged-in user
        r = self.app.get('/manage-users')
        reg_exp = re.search(
            '<td>Test User<\/td>(.|\n)*?<td><a href="(\/create-edit-user\?id=([0-9]+))">', r.data)
        disable_user_id = reg_exp.group(3)
        r = self.app.post('/create-edit-user', data=dict(
            update_id=disable_user_id,
            name='Milton Waddams',
            email='Milton@waddams.com',
            password='',
            active=False
        ), follow_redirects=True)
        print(r.data)
        r = self.app2.get('/')
        """
        assert False

    # Test Cases - Sitewide Stuff
    def test_site_settings(self):
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

if __name__ == '__main__':
    unittest.main()