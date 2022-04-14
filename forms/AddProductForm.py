from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired


class AddProductsForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    cost = IntegerField('Cost', validators=[DataRequired()])
    submit_2 = SubmitField('Submit')
