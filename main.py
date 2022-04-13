from flask import Flask, request
from flask import render_template, redirect
from flask_login import login_user, LoginManager, login_required, logout_user, current_user
from flask_restful import Api
from requests import delete, post, patch, get
from werkzeug.exceptions import Unauthorized

from data import db_session, users_resource, recipes_resources
from data.products import Products
from data.recipes import Recipes
from data.users import User
from forms.AddRecipeForm import AddRecipeForm
from forms.FinderForm import FinderForm
from forms.LoginForm import LoginForm
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
    log_writer(error)
    return redirect("/login")


def main():
    db_session.global_init("db/mars_explorer.db")

    api.add_resource(users_resource.UsersListResource, '/api/v2/users')
    api.add_resource(users_resource.UsersResource, '/api/v2/users/<int:user_id>')

    api.add_resource(recipes_resources.RecipesResource, '/api/recipe/<int:recipe_id>')
    api.add_resource(recipes_resources.RecipesListResource, '/api/recipe')
    app.run()


@app.route('/products', methods=['GET', 'POST'])
@login_required
def products():
    form = FinderForm()
    product = None

    if form.validate_on_submit() and form.submit.data:
        db_sess = db_session.create_session()
        search = form.name.data[1:]
        results = db_sess.query(Products).all()
        for element in results:
            if search in element.name:
                product = element

    return render_template("Products.html", form=form, product=product)


@app.route('/recipes_delete/<int:id_recipe>', methods=['GET', 'POST'])
@login_required
def recipe_delete(id_recipe):
    """:param id_recipe recipe, that will be deleted
       :return redirects to main recipe page"""
    delete(f'http://localhost:5000/api/recipe/{id_recipe}').json()
    log_writer(f'http://localhost:5000/api/recipe/{id_recipe}')
    return redirect('/recipes')


@app.route("/recipes_edit/<int:id_recipe>", methods=['GET', "POST"])
@login_required
def recipe_edit(id_recipe):
    results = get(f'http://localhost:5000/api/recipe/{id_recipe}').json()['recipe']
    edit_form = AddRecipeForm()

    if request.method == 'GET':
        edit_form.name.data = results['name']
        edit_form.content.data = results['content']
        edit_form.products.data = results['products']
        edit_form.caloric.data = results['caloric_content']

    if edit_form.validate_on_submit() and edit_form.submit_2.data:
        if 'file' in request.files:
            f = request.files['file']
            if f.filename == '':
                im_name = results['image']
            else:
                f.save(f'static/img/{f.filename}')
                im_name = f'static/img/{f.filename}'
        else:
            im_name = results['image']

        patch(f'http://localhost:5000/api/recipe/{id_recipe}', json={'name': edit_form.name.data,
                                                                     'content': edit_form.content.data,
                                                                     'products': edit_form.products.data,
                                                                     'caloric': int(edit_form.caloric.data),
                                                                     'image': im_name,
                                                                     'owner_id': int(current_user.id)}).json()

        log_writer(f'http://localhost:5000/api/recipe/{id_recipe}')
        return redirect('/recipes')

    return render_template("Recipes_edit.html", form=edit_form)


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

            log_writer('http://localhost:5000/api/recipe')

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

        log_writer('http://localhost:5000/api/v2/users')

        return redirect('/login')
    return render_template('Registration.html', title='Регистрация', form=form)


def log_writer(line):
    error = ['', '--------', line, '--------', '']
    print(*error, sep='\n')


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
