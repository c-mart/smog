SMOG: Simple Markdown blOG

Like the Flaskr blog but better.

- Sqlite3 backend for now, something better later
- One user account for now, table of users with salted/hashed passwords later
- Manual forms now, WTForms later

Database migration to expand schema, add an "author" field to posts

## Tests to write
- Logging in and posting
- Trying to use an invalid user ID
- Test logging in wrong all sorts of ways

## Technique/Style Questions
`first_or_404()` or `try: return User.query.filter_by(id=int(user_id)).one() except NoResultFound():`?

## Todo
- Why does my app throw OperationalErrors after running test cases?
- Handle "next" for login
- Relationship between users and posts. Each post has an "author".
- Write some tests
- Make some CSS
- Published checkbox should be true by default
- Preview?
- Post type can be post (shown serially in date order) or static page (shown in nav)
- Mitigate XSS and CSRF
- create_edit_post() does a LOT. would it be better to split this into multiple views?

x Show admin (post, edit, delete) buttons if logged in
x Only allow post/edit/delete view if logged in
x Line breaks aren't showing - just render markdown
x Allow viewing of drafts
x Allow editing post where post is updated
x Allow editing post which updates edit date but not create date
x make password form box hidden

## Extended Features
- Confirm before deleting post
- Switch to another Markdown renderer (http://lepture.com/en/2014/markdown-parsers-in-python) which supports footnotes
- Figure out markdown blockquoting
- Static pages separate from posts
- Automatically publish at a date and time
- Preview function while composing
- Built-in image hosting with exif tag removal
- People can post comments
- Comment moderation
- Post tags with tag cloud
- RSS