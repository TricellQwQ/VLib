from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired
from wtforms import StringField, TextAreaField
from wtforms import SubmitField
from wtforms.validators import DataRequired


class BookOpenlibForm(FlaskForm):
    openlibid = StringField("Open Library ISBN", validators=[DataRequired()])
    description = TextAreaField("Description")
    content = TextAreaField("Content")
    submit = SubmitField("Sumbit")