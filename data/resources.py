from flask_restful import abort

from data import db_session
from data.recipes import Recipes
from data.users import User
from data.products import Products


def abort_if_user_not_found(user_id):
    session = db_session.create_session()
    users = session.query(User).get(user_id)
    if not users:
        abort(404, message=f"User {user_id} not found")


def abort_if_recipe_not_found(recipe_id):
    session = db_session.create_session()
    recipes = session.query(Recipes).get(recipe_id)
    if not recipes:
        abort(404, message=f"Recipe {recipe_id} not found")


def abort_if_products_not_found(product_id):
    session = db_session.create_session()
    products = session.query(Products).get(product_id)
    if not products:
        abort(404, message=f"Product {product_id} not found")