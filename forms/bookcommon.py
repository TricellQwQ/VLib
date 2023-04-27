from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired
from wtforms import StringField, TextAreaField
from wtforms import SubmitField
from wtforms.validators import DataRequired


class BookCommonForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    description = TextAreaField("Description")
    content = TextAreaField("Content")
    author = StringField("Author", validators=[DataRequired()])
    submit = SubmitField("Sumbit")