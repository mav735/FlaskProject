from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, EmailField, IntegerField
from wtforms.validators import DataRequired
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class RegisterForm(FlaskForm, UserMixin):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    surname = StringField('Фамилия пользователя', validators=[DataRequired()])
    name = StringField('Имя пользователя', validators=[DataRequired()])
    age = IntegerField('Возраст', validators=[DataRequired()])
    position = StringField('Должность', validators=[DataRequired()])
    speciality = StringField('Профессия', validators=[DataRequired()])
    address = StringField('Адрес', validators=[DataRequired()])
    submit = SubmitField('Войти')
