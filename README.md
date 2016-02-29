# smog
Simple Markdown blOG, or chriS Martin's blOG

- Built with Python using Flask microframework
- Write posts in Markdown or HTML
- SQLAlchemy with modular back-end, use any database you want
- HTML5
- Renders nicely without JavaScript because there is no JavaScript
- GNU GPL

For demo blog, see https://update.me.later

## Story
I wrote this in order to learn Python web development and scratch a personal itch for a blogging engine.

## Documentation

## Acknowledgements
- Mistune Markdown interpreter
- Default template uses https://en.wikipedia.org/wiki/Tango_Desktop_Project#Palette

## Known Issues
- We're not adequately protecting against CSRF. Plan to switch to WTForms.
- Currently no separation of privileges between users. Any user can CRUD other user accounts. (This isn't a problem if there is only one user or all users trust each other.)
- When a user account is disabled, the disabled user is not prevented from doing anything until he or she logs out. Until this is fixed, smog is probably not a good choice for folks that want the ability to instantly shut off a given user's access.

## Dependencies
flask-Misaka needs python-dev, libffi-dev

## License
Copyright 2016 Chris Martin. smog is free software released under the GNU GPL version 3.