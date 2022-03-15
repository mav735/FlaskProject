from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, EmailField
from wtforms import SubmitField
from wtforms.validators import DataRequired


class DepartmentsForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    chief = IntegerField("Id лидера")
    members = StringField('Участники', validators=[DataRequired()])
    email = EmailField("Почта")
    submit = SubmitField('Отправить')
