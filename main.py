import datetime

from flask import Flask, request, make_response, jsonify
from flask import render_template, redirect
from flask_login import login_user, LoginManager, login_required, logout_user, current_user
from flask_restful import abort, Api
from werkzeug.exceptions import abort

from requests import get, delete, post, patch

from data import db_session, news_resources, users_resource
from data.jobs import Jobs
from data.news import News
from data.users import User
from forms.JobsForm import JobsForm
from forms.LoginForm import LoginForm
from forms.NewsForm import NewsForm
from forms.user import RegisterForm

app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), error)


def main():
    db_session.global_init("db/mars_explorer.db")
    api.add_resource(news_resources.NewsListResource, '/api/news')
    api.add_resource(news_resources.NewsResource, '/api/news/<int:news_id>')

    api.add_resource(users_resource.UsersListResource, '/api/v2/users')
    api.add_resource(users_resource.UsersResource, '/api/v2/users/<int:user_id>')
    app.run()


@app.route('/all_news')
def all_news():
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        news = db_sess.query(News).filter(
            (News.user_id == current_user.id) | (News.is_private != 1))
    else:
        news = db_sess.query(News).filter(News.is_private == 0)

    return render_template('show_news.html', news=news)


@app.route('/news', methods=['GET', 'POST'])
@login_required
def add_news():
    form = NewsForm()
    if form.validate_on_submit():
        post('http://localhost:5000/api/news', json={
            "title": form.title.data,
            "content": form.content.data,
            "is_private": form.is_private.data,
            "user_id": current_user.id
        }).json()
        return redirect('/')
    return render_template('news.html', title='Добавление новости',
                           form=form)


@app.route('/news/<int:news_id>', methods=['GET', 'POST'])
@login_required
def edit_news(news_id):
    form = NewsForm()
    if request.method == "GET":
        result = get(f'http://localhost:5000/api/news/{news_id}').json()['news']
        form.title.data = result['title']
        form.content.data = result['content']
        form.is_private.data = result['is_private']
    if form.validate_on_submit():
        patch(f'http://localhost:5000/api/news/{news_id}', json={"title": form.title.data,
                                                                 "content": form.content.data,
                                                                 "is_private": form.is_private.data}).json()
        return redirect('/')
    return render_template('news.html',
                           title='Редактирование новости',
                           form=form
                           )


@app.route('/news_delete/<int:id_news>', methods=['GET', 'POST'])
@login_required
def news_delete(id_news):
    delete(f'http://localhost:5000/api/news/{id_news}').json()
    return redirect('/')


@app.route('/jobs/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_jobs(id):
    form = JobsForm()
    print(form)
    if request.method == "GET":
        db_sess = db_session.create_session()
        jobs = db_sess.query(Jobs).filter(Jobs.id == id).first()
        if jobs:
            form.job.data = jobs.job
            form.work_size.data = int(jobs.work_size)
            form.is_finished.data = jobs.is_finished
            form.collaborators.data = jobs.collaborators
            form.team_leader.data = int(jobs.team_leader)
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        jobs = db_sess.query(Jobs).filter(Jobs.id == id).first()

        if jobs:
            jobs.job = form.job.data
            jobs.work_size = int(form.work_size.data)
            jobs.is_finished = form.is_finished.data
            jobs.collaborators = form.collaborators.data
            jobs.team_leader = int(form.team_leader.data)
            jobs.start_date = datetime.datetime.now()
            jobs.end_date = datetime.datetime.now()
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('add_job.html',
                           title='Редактирование работы',
                           form=form
                           )


@app.route('/jobs_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def jobs_delete(id):
    db_sess = db_session.create_session()
    jobs = db_sess.query(Jobs).filter(Jobs.id == id).first()
    if jobs:
        db_sess.delete(jobs)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/add_job', methods=['GET', 'POST'])
@login_required
def add_jobs():
    form = JobsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        jobs = Jobs()
        jobs.job = form.job.data
        jobs.work_size = int(form.work_size.data)
        jobs.is_finished = form.is_finished.data
        jobs.collaborators = form.collaborators.data
        jobs.team_leader = int(form.team_leader.data)
        jobs.start_date = datetime.datetime.now()
        jobs.end_date = datetime.datetime.now()
        db_sess.add(jobs)
        db_sess.commit()
        db_sess.close()
        return redirect('/')
    return render_template('add_job.html', title='Добавление работы',
                           form=form)


@app.route("/")
def work_log():
    db_sess = db_session.create_session()
    param = {"jobs": []}
    for el in db_sess.query(Jobs).all():
        job = {"id": el.id, "job": el.job,
               "team_leader": db_sess.query(User).filter(
                   User.id == el.team_leader).first().surname + ' ' + db_sess.query(User).filter(
                   User.id == el.team_leader).first().name,
               "team_leader_id": el.team_leader,
               "collaborators": el.collaborators, "finished": el.is_finished}
        if el.is_finished:
            job["duration"] = el.end_date - el.start_date
        else:
            job["duration"] = datetime.datetime.now() - el.start_date

        param["jobs"].append(job)
    return render_template("index.html", **param)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        post('http://localhost:5000/api/v2/users', json={
            'surname': form.surname.data,
            'name': form.name.data,
            'age': form.age.data,
            'address': form.address.data,
            'speciality': form.speciality.data,
            'position': form.position.data,
            'email': form.email.data,
            'password': form.password.data}).json()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


if __name__ == '__main__':
    main()
