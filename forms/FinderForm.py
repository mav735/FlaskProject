from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class FinderForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Find')
