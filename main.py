import datetime
import os

from flask import Flask, request
from flask import render_template, redirect
from flask_login import login_user, LoginManager, login_required, logout_user, current_user
from flask_restful import abort, Api
from werkzeug.exceptions import abort, Unauthorized

from requests import get, delete, post, patch
from werkzeug.utils import secure_filename

from data import db_session, news_resources, users_resource, jobs_resources, recipes_resources
from data.jobs import Jobs
from data.news import News
from data.users import User
from data.recipes import Recipes
from data.products import Products
from forms.FinderForm import FinderForm
from forms.JobsForm import JobsForm
from forms.LoginForm import LoginForm
from forms.NewsForm import NewsForm
from forms.AddRecipeForm import AddRecipeForm
from forms.user import RegisterForm

UPLOAD_FOLDER = '/static/img'
app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.errorhandler(Unauthorized)
def Unauthorized(error):
    print(error)
    return redirect("/login")


def main():
    db_session.global_init("db/mars_explorer.db")

    api.add_resource(news_resources.NewsListResource, '/api/news')
    api.add_resource(news_resources.NewsResource, '/api/news/<int:news_id>')

    api.add_resource(users_resource.UsersListResource, '/api/v2/users')
    api.add_resource(users_resource.UsersResource, '/api/v2/users/<int:user_id>')

    api.add_resource(jobs_resources.JobsListResource, '/api/v2/jobs')
    api.add_resource(jobs_resources.JobsResource, '/api/v2/jobs/<int:job_id>')

    api.add_resource(recipes_resources.RecipesResource, '/api/recipe/<int:recipe_id>')
    api.add_resource(recipes_resources.RecipesListResource, '/api/recipe')
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


@app.route('/jobs_delete/<int:job_id>', methods=['GET', 'POST'])
@login_required
def jobs_delete(job_id):
    delete(f'http://localhost:5000/api/v2/jobs/{job_id}').json()
    return redirect('/')


@app.route('/add_job', methods=['GET', 'POST'])
@login_required
def add_jobs():
    form = JobsForm()
    if form.validate_on_submit():
        post('http://localhost:5000/api/v2/jobs', json={'job': form.job.data,
                                                        'work_size': int(form.work_size.data),
                                                        'collaborators': form.collaborators.data,
                                                        'is_finished': bool(form.is_finished.data),
                                                        'team_leader': int(form.team_leader.data)}).json()
        return redirect('/')
    return render_template('add_job.html', title='Добавление работы',
                           form=form)


@app.route("/recipes", methods=('GET', 'POST'))
@login_required
def recipes():
    form = FinderForm()
    add_form = AddRecipeForm()
    recipe = None

    if form.validate_on_submit() and form.submit.data:
        db_sess = db_session.create_session()
        search = form.name.data[1:]
        results = db_sess.query(Recipes).all()
        for element in results:
            if search in element.name:
                recipe = element
        return render_template("Recipes.html", form=form, add_form=add_form, recipe=recipe)

    if add_form.validate_on_submit() and add_form.submit_2.data:
        if 'file' in request.files:
            f = request.files['file']
            f.save(f'static/img/{f.filename}')

            post('http://localhost:5000/api/recipe', json={'name': add_form.name.data,
                                                           'content': add_form.content.data,
                                                           'products': add_form.products.data,
                                                           'caloric': int(add_form.caloric.data),
                                                           'image': f'static/img/{f.filename}',
                                                           'owner_id': int(current_user.id)}).json()

        form = FinderForm()
        add_form = AddRecipeForm()

        return render_template("Recipes.html", form=form, add_form=add_form, recipe=recipe)

    return render_template("Recipes.html", form=form, add_form=add_form, recipe=recipe)


@app.route("/")
def work_log():
    return render_template("index.html", current_user=current_user)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Registration',
                                   form=form,
                                   message="Passwords")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Registration',
                                   form=form,
                                   message="Такой пользователь уже есть")
        post('http://localhost:5000/api/v2/users', json={
            'login': form.login.data,
            'email': form.email.data,
            'password': form.password.data}).json()
        return redirect('/login')
    return render_template('Registration.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/recipes")
        return render_template('Login.html',
                               message="Incorrect login or password",
                               form=form)
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


if __name__ == '__main__':
    main()
