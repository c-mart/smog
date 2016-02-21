SMOG: Simple Markdown blOG

Like the Flaskr blog but better.

- Sqlite3 backend for now, something better later
- Manual forms now, WTForms later

## Tests to write
- Test trying to load an unpublished post by its permalink

## Todo
- Make some CSS

- CRUD users, let users change password
- How should I handle posting with special characters in title and no permalink field?
- Render description in HTML somewhere. Consider separate template for showing single post with meta tag
- Handle "next" for login
- Published checkbox should be true by default
- Preview?
- Post type can be post (shown serially in date order) or static page (shown in nav)
- Mitigate XSS and CSRF
- create_edit_post() does a LOT. would it be better to split this into multiple views?

x Relationship between users and posts. Each post has an "author".
x Database migration to expand schema, add an "author" field to posts
x Why does my app throw OperationalErrors after running test cases? Because testing was using a separate database
x Show admin (post, edit, delete) buttons if logged in
x Only allow post/edit/delete view if logged in
x Line breaks aren't showing - just render markdown
x Allow viewing of drafts
x Allow editing post where post is updated
x Allow editing post which updates edit date but not create date
x make password form box hidden
x Write some tests

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