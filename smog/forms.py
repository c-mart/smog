from flask_wtf import Form, RecaptchaField
from wtforms import StringField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, Email, Length


class CommentForm(Form):
    """Comment form for logged-in user."""
    body = TextAreaField('Comment body', validators=[DataRequired(), Length(min=5)])


class CommentFormGuest(CommentForm):
    """Comment form for guest, inherits from base CommentForm."""
    guest_author_name = StringField('Name', default=None, validators=[DataRequired()])
    guest_author_email = StringField('Email', default=None, validators=[DataRequired(), Email()])
    recaptcha = RecaptchaField()


class CommentFormEditGuest(CommentFormGuest):
    """Form for editing a guest comment with no recaptcha field, because this is only presented to trusted users."""
    guest_author_name = StringField('Name', default=None, validators=[DataRequired()])
    guest_author_email = StringField('Email', default=None, validators=[DataRequired(), Email()])
    recaptcha = None
