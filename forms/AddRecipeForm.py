from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired


class AddRecipeForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    content = StringField('Content', validators=[DataRequired()])
    products = StringField('Products', validators=[DataRequired()])
    caloric = IntegerField('Caloric Content', validators=[DataRequired()])
    submit_2 = SubmitField('Add Recipe')
