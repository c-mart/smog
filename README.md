# smog
Simple Markdown blOG, or chriS Martin's blOG

- Built with Python using Flask microframework
- Write posts in Markdown or HTML
- SQLAlchemy with modular back-end, use any database you want
- HTML5
- Renders nicely without JavaScript because there is no JavaScript
- GNU GPL

For demo blog, see https://update.me.later

## Documentation
Mikasa Markdown interpreter: https://flask-misaka.readthedocs.org/en/latest/

## Known Issues
- We're not adequately protecting against CSRF. Plan to switch to WTForms.
- Currently no separation of privileges between users. Any user can CRUD other user accounts. (This isn't a problem if there is only one user or all users trust each other.)

## Dependencies
flask-Misaka needs python-dev, libffi-dev

## License
Copyright 2016 Chris Martin. smog is free software released under the GNU GPL version 3.