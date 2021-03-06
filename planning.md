SMOG: Simple Markdown blOG

## To do
Consider deploying entire site using docker, which means I need a WSGI server and a database container?
Remove my ReCAPTCHA API keys from config_default.py?
Fix tests which break when we start with a test post in database

## CSS Fixes
- Centered caption under images

## Todo
- WTForms for other forms on site, not just comments
- Alternative to recaptcha for people without JavaScript
- Unpublished post should have a flash message saying "not published"
- Atom feed for comments
- https://flask-wtf.readthedocs.org/en/latest/csrf.html#why-csrf
- How to order static pages?
- H2 in post title and in post body look the same, they should be different? Render H2s in post body as H3s when?
- Handle "next" for login
- create_edit_post() does a LOT. would it be better to split this into multiple views, one for create and one for edit?
- Standardize nomenclature of "nav"/"navigation" vs "site menu" throughout codebase
- Standardize nomenclature of "timeline" vs "home page" vs "posts page"
- Standardize nomenclature of "active"/"inactive" vs "enabled"/"disabled" user account in model

## Extended Features todo
- Post author receives email notifications on new comments
- Subscribe to comments via email
- Preview function while composing, pagedown
- Post tags with tag cloud
- Confirm before deleting post
- Automatically publish at a date and time

## Completed Todo
- Show description (without images) in site index
- Down arrow in CSS dropdown buttons
- HR after post in single post page should come before "posted on" footer
- All posts should show as table
- Center images inside posts?
- Make log in/out link float to right of top nav bar
- Admin menu should be a drop-down toward right of top nav bar
- Find a better markdown quick reference. Should I write one?
- "Post successful" should bring us back to single-page post
- Make "Full post and comments" link better
- Fix display of bullets in post body
- Images should scale down on small displays
- Nav bar should not look like a browser toolbar
- Fix regular font size, make it a little bigger
- Change delete URL to "delete_post" for clarity
- Rename create_edit.html to create_edit_post.html
- Refactor "Active" user to "Enabled" user in templates to resolve ambiguity
- Redirect poster to permalink after posting
- Test for posting static pages vs blog post
- HR BETWEEN POST AND COMMENTS
- Link to Markdown reference in create post page, perhaps instructions to insert an image
- Site settings should have a place to insert analytics tracking code at the footer of each page (e.g. for Piwik or Google Analytics)
- Learn about database migrations. Rolling out new feature (ability to set analytics tracking code in site settings) to existing deployment requires something like https://flask-migrate.readthedocs.org/en/latest/
- Work on update-ability. Currently, running "git clone" overwrites the config (e.g. database URI) on a running web server. Learn best practices of how this is handled with production apps.
- Switch to another Markdown renderer (http://lepture.com/en/2014/markdown-parsers-in-python) which supports footnotes and is implemented in pure python
- Don't allow user to deactivate or delete him/her self
- Some kind of better user management
- Render description in HTML somewhere. Consider separate template for showing single post with meta tag
- Set browser title bar
- Settings page with configurable blog title, footer string (e.g. "Copyright Bob Loblaw $currentyear"). Perhaps just load these into environment variables.
- RSS/Atom feed (I did Atom)
- "All Posts" page which lists posts in reverse chronological order
- static pages.
- Test for use of slugify, ensure permalinks are cleaned up
- How should I handle posting with special characters in title and no permalink field?
- Get rid of green in CSS
- Strip non-alphanumeric characters from permalinks
- Test trying to load an unpublished post by its permalink
- How do deal with H1? Single-post page has post title as H1. Multiple-post page has blog title as H1.
- Published checkbox should be true by default
- Relationship between users and posts. Each post has an "author".
- Database migration to expand schema, add an "author" field to posts
- Why does my app throw OperationalErrors after running test cases? Because testing was using a separate database
- Show admin (post, edit, delete) buttons if logged in
- Only allow post/edit/delete view if logged in
- Line breaks aren't showing - just render markdown
- Allow viewing of drafts
- Allow editing post where post is updated
- Allow editing post which updates edit date but not create date
- make password form box hidden
- Write some tests
- Static pages separate from posts
- People can post comments, comment moderation
- Demo site
- Table layout for All Posts page
- Figure out markdown blockquoting and footnotes