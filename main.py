import os

import pandas
from flask import Flask, request
from flask import render_template, redirect
from flask_login import login_user, LoginManager, login_required, logout_user, current_user
from flask_restful import Api
from requests import delete, post, patch, get
from werkzeug.exceptions import Unauthorized
from data import db_session, users_resource, recipes_resources, products_resources
from data.products import Products
from data.recipes import Recipes
from data.users import User
from forms.AddProductForm import AddProductsForm
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


def excel_products():
    db_sess = db_session.create_session()
    results = db_sess.query(Products).all()
    result_dict = {'Id': [], 'Name': []}
    for element in results:
        result_dict['Id'].append(element.id)
        result_dict['Name'].append(element.name)

    form = pandas.DataFrame(result_dict)
    form.to_excel('static/Products.xlsx')


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

    api.add_resource(products_resources.ProductsResource, '/api/product/<int:product_id>')
    api.add_resource(products_resources.ProductsListResource, '/api/product')

    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


@app.route("/products_edit/<int:id_product>", methods=['GET', "POST"])
@login_required
def product_edit(id_product):
    results = get(f'http://localhost:5000/api/product/{id_product}').json()['product']
    edit_form = AddProductsForm()

    if request.method == 'GET':
        edit_form.name.data = results['name']
        edit_form.cost.data = results['cost']

    if edit_form.validate_on_submit() and edit_form.submit_2.data:
        patch(f'http://localhost:5000/api/product/{id_product}',
              json={'name': edit_form.name.data,
                    'cost': edit_form.cost.data}).json()

        log_writer(f'http://localhost:5000/api/product/{id_product}')
        return redirect('/products')

    return render_template("Products_edit.html", form=edit_form)


@app.route('/add_to_favourite/<int:id_recipe>', methods=['GET', 'POST'])
@login_required
def add_favourite(id_recipe):
    db_sess = db_session.create_session()
    results = db_sess.query(User).get(current_user.id)
    if results.favourite_recipes_ids is not None:
        recipes_data = list(filter(lambda x: x != '', results.favourite_recipes_ids.split(', ')))
        recipes_data.append(str(id_recipe))
        results.favourite_recipes_ids = ', '.join(recipes_data)
    else:
        results.favourite_recipes_ids = f'{id_recipe}, '
    db_sess.commit()
    return redirect('/recipes')


@app.route('/clear_favourite')
@login_required
def clear_products():
    db_sess = db_session.create_session()
    results = db_sess.query(User).get(current_user.id)
    results.favourite_recipes_ids = ''
    db_sess.commit()
    return redirect('/recipes')


@app.route('/shop')
@login_required
def shop():
    db_sess = db_session.create_session()
    results = db_sess.query(User).get(current_user.id)
    products_data = []
    recipes_dict = {}
    if results.favourite_recipes_ids is not None:
        recipes_data = list(filter(lambda x: x != '', results.favourite_recipes_ids.split(', ')))
        for element in recipes_data:
            if element in recipes_dict.keys():
                recipes_dict[element][0] += 1
            else:
                recipes_dict[element] = [1]

        for element in recipes_dict.keys():
            results = db_sess.query(Recipes).get(int(element))
            if results is not None:
                for pr in list(map(int, results.products.split(', '))):
                    products_data.append(pr)

                recipes_dict[element].append(results.cost * recipes_dict[element][0])
                recipes_dict[element].append(results.caloric_content * recipes_dict[element][0])
                recipes_dict[element].insert(0, results.name)
            else:
                recipes_data.pop(recipes_data.index(element))
                user = db_sess.query(User).get(current_user.id)
                user.favourite_recipes_ids = ', '.join(recipes_data)
                db_sess.commit()

        poped = []
        for element in recipes_dict.keys():
            if len(recipes_dict[element]) < 3:
                poped.append(element)

        for element in poped:
            recipes_dict.pop(element)

        result_products_dict = {'Id': [], 'Name': [], 'Amount': [], 'Cost': []}

        for element in products_data:
            db_sess = db_session.create_session()
            results = db_sess.query(Products).get(element)
            if results is not None:
                if results.id not in result_products_dict['Id']:
                    result_products_dict['Id'].append(results.id)
                    result_products_dict['Name'].append(results.name)
                    counter = 0
                    for part in products_data:
                        if part == results.id:
                            counter += 1
                    result_products_dict['Amount'].append(counter)
                    result_products_dict['Cost'].append(counter * results.cost)

        result_products_dict.pop('Id')
        result_products_dict['Name'].append('Total:')
        result_products_dict['Amount'].append(sum(result_products_dict['Amount']))
        result_products_dict['Cost'].append(str(sum(result_products_dict['Cost'])) + ' Rubles')
        form = pandas.DataFrame(result_products_dict)
        form.to_excel('static/Results.xlsx')

    return render_template('Shop.html', recipes_data=recipes_dict)


@app.route('/products', methods=['GET', 'POST'])
@login_required
def products():
    excel_products()

    form = FinderForm()
    additional_form = AddProductsForm()
    product = None

    if form.validate_on_submit() and form.submit.data:
        db_sess = db_session.create_session()
        search = form.name.data[1:]
        results = db_sess.query(Products).all()
        for element in results:
            if search in element.name:
                product = element

    if additional_form.validate_on_submit() and additional_form.submit_2.data:
        post('http://localhost:5000/api/product', json={'name': additional_form.name.data,
                                                        'cost': additional_form.cost.data}).json()

        log_writer('http://localhost:5000/api/product')

        form = FinderForm()
        additional_form = AddProductsForm()

    return render_template("Products.html", form=form, additional_form=additional_form, product=product)


@app.route('/products_delete/<int:id_product>', methods=['GET', 'POST'])
@login_required
def product_delete(id_product):
    """:param id_product product, that will be deleted
       :return redirects to main product page"""
    delete(f'http://localhost:5000/api/product/{id_product}').json()

    log_writer(f'http://localhost:5000/api/product/{id_product}')

    return redirect('/products')


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

        if recipe is not None:
            products_names = []

            prod = recipe.products.split(', ')
            recipe_cost = 0
            for element in prod:
                now = db_sess.query(Products).get(int(element))
                if now is not None:
                    recipe_cost += now.cost
                    products_names.append(now.name)
            recipe.cost = recipe_cost
            db_sess.commit()

            return render_template("Recipes.html",
                                   form=form,
                                   add_form=add_form,
                                   recipe=recipe,
                                   products_names=products_names,
                                   len_products=len(products_names))

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
    try:
        db_sess = db_session.create_session()
        results = db_sess.query(User).get(current_user.id)
    except AttributeError:
        results = None
    return render_template("index.html", current_user=results)


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
    excel_products()
