SMOG: Simple Markdown blOG
Like the Flaskr blog but better.

- Sqlite3 backend for now, something better later
- Manual forms now, WTForms later

## Ship-critical issues to fix
- Rename create_edit.html to create_edit_post.html
- Some kind of better user management
- Don't allow user to deactivate or delete him/her self
- Fix CSS for flash messages
- More space between post-footer-items?
- Clean up presentation of create/edit form for static page options
- Don't show title twice for single-post page

## Todo
- Refactor "Active" user to "Enabled" user to resolve ambiguity
- Mitigate XSS and CSRF using WTForms
- Redirect poster to permalink after posting
- Test for posting static pages vs blog post
- How to order static pages?
- Center images inside posts?
- H2 in post title and in post body look the same, they should be different? Render H2s in post body as H3s when?
- Handle "next" for login
- Post type can be post (shown serially in date order) or static page (shown in nav)
- create_edit_post() does a LOT. would it be better to split this into multiple views?
- Make form fields light on dark

## Completed Todo
x Render description in HTML somewhere. Consider separate template for showing single post with meta tag
x Set browser title bar
x Settings page with configurable blog title, footer string (e.g. "Copyright Bob Loblaw $currentyear"). Perhaps just load these into environment variables.
x RSS/Atom feed (I did Atom)
x "All Posts" page which lists posts in reverse chronological order
x static pages.
x Test for use of slugify, ensure permalinks are cleaned up
x How should I handle posting with special characters in title and no permalink field?
x Get rid of green in CSS
x Strip non-alphanumeric characters from permalinks
x Test trying to load an unpublished post by its permalink
x How do deal with H1? Single-post page has post title as H1. Multiple-post page has blog title as H1.
x Published checkbox should be true by default
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
- Two column layout for All Posts page
- Post tags with tag cloud
- Confirm before deleting post
- Switch to another Markdown renderer (http://lepture.com/en/2014/markdown-parsers-in-python) which supports footnotes and is implemented in pure python
- Figure out markdown blockquoting
- Static pages separate from posts
- Automatically publish at a date and time
- Preview function while composing
- Built-in image hosting with exif tag removal
- People can post comments, comment moderation
- Allow short post URLs with post ID