SMOG: Simple Markdown blOG

Like the Flaskr blog but better.

- Sqlite3 backend for now, something better later
- One user account for now, table of users with salted/hashed passwords later
- Manual forms now, WTForms later

## Todo
- Published checkbox should be true by default
- Preview?
- Post type can be post (shown serially in date order) or static page (shown in nav)
- Show admin (post, edit, delete) buttons if logged in
- Only allow post/edit/delete view if logged in
- Blockquoting
- Mitigate XSS and CSRF
- create_edit_post() does a LOT. would it be better to split this into multiple views?

x Line breaks aren't showing - just render markdown
x Allow viewing of drafts
x Allow editing post where post is updated
x Allow editing post which updates edit date but not create date


## Core Features
- Written in HTML5
- Front page for users
- Admin area to CRUD posts
- Posts written in markdown and parsed as HTML. HTML in posts OK too
- Published True/False for drafting posts but not showing them
- RSS
- Test-driven

## Extended Features
- Static pages separate from posts
- Preview function while composing
- Built-in image hosting with exif tag removal
- People can post comments
- Comment moderation
- Post tags with tag cloud
- Tweakable