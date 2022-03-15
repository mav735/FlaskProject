import datetime

from flask_login import login_user, LoginManager, login_required, logout_user, current_user
from werkzeug.exceptions import abort

from data import db_session
from data.departments import Department
from data.news import News
from data.users import User
from data.jobs import Jobs
from flask import Flask, request
from flask import render_template, redirect

from forms.DepartmentForm import DepartmentsForm
from forms.JobsForm import JobsForm
from forms.NewsForm import NewsForm
from forms.user import RegisterForm
from forms.LoginForm import LoginForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


def main():
    db_session.global_init("db/mars_explorer.db")
    app.run()


@app.route('/all_news')
def all_news():
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        news = db_sess.query(News).filter(
            (News.user == current_user) | (News.is_private != 1))
    else:
        news = db_sess.query(News).filter(News.is_private != 1)

    return render_template('show_news.html', news=news)


@app.route('/all_departments')
def all_departments():
    db_sess = db_session.create_session()
    param = {"departments": []}
    for el in db_sess.query(Department).all():
        department = {"id": el.id, "title": el.title,
                      "chief": db_sess.query(User).filter(
                          User.id == el.chief).first().surname + ' ' + db_sess.query(User).filter(
                          User.id == el.chief).first().name,
                      "chief_id": el.chief,
                      "members": el.members,
                      "email": el.email}

        param["departments"].append(department)
    return render_template('show_departments.html', **param)


@app.route('/add_department', methods=['GET', 'POST'])
@login_required
def add_departments():
    form = DepartmentsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        departments = Department()
        departments.title = form.title.data
        departments.email = form.email.data
        departments.chief = form.chief.data
        departments.members = form.members.data
        db_sess.add(departments)
        db_sess.commit()
        db_sess.close()
        return redirect('/all_departments')
    return render_template('add_department.html', title='Добавление департамента',
                           form=form)


@app.route('/departments/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_departments(id):
    form = DepartmentsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        departments = db_sess.query(Department).filter(Department.id == id).first()
        if departments:
            form.title.data = departments.title
            form.chief.data = int(departments.chief)
            form.email.data = departments.email
            form.members.data = departments.members
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        departments = db_sess.query(Department).filter(Department.id == id).first()
        if departments:
            departments.title = form.title.data
            departments.chief = int(form.chief.data)
            departments.email = form.email.data
            departments.members = form.members.data
            db_sess.commit()
            return redirect('/all_departments')
        else:
            abort(404)
    return render_template('add_department.html',
                           title='Редактирование работы',
                           form=form
                           )


@app.route('/departments_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def departments_delete(id):
    db_sess = db_session.create_session()
    departments = db_sess.query(Department).filter(Department.id == id).first()
    if departments:
        db_sess.delete(departments)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/all_departments')


@app.route('/news', methods=['GET', 'POST'])
@login_required
def add_news():
    form = NewsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = News()
        news.title = form.title.data
        news.content = form.content.data
        news.is_private = form.is_private.data
        current_user.news.append(news)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('news.html', title='Добавление новости',
                           form=form)


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


@app.route('/news/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    form = NewsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
        if news:
            form.title.data = news.title
            form.content.data = news.content
            form.is_private.data = news.is_private
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
        if news:
            news.title = form.title.data
            news.content = form.content.data
            news.is_private = form.is_private.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('news.html',
                           title='Редактирование новости',
                           form=form
                           )


@app.route('/news_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.id == id,
                                      News.user == current_user
                                      ).first()
    if news:
        db_sess.delete(news)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


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
        user = User(
            surname=form.surname.data,
            name=form.name.data,
            position=form.position.data,
            speciality=form.speciality.data,
            address=form.address.data,
            email=form.email.data,
            modified_date=datetime.datetime.now()
        )

        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
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
