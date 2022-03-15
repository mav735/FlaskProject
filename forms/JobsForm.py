from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DateTimeField
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired


class JobsForm(FlaskForm):
    job = StringField('Название', validators=[DataRequired()])
    work_size = IntegerField("Объем работы")
    collaborators = StringField('Участники', validators=[DataRequired()])
    is_finished = BooleanField("Работа закончена")
    team_leader = IntegerField('Id лидера', validators=[DataRequired()])
    submit = SubmitField('Применить')
