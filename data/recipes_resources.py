from flask import jsonify
from flask_restful import Resource, reqparse

from data import db_session
from data.recipes import Recipes
from data.resources import abort_if_recipe_not_found


class RecipesResource(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('name', required=True)
        self.parser.add_argument('content', type=int, required=True)
        self.parser.add_argument('products', required=True)
        self.parser.add_argument('cost', type=bool, required=True)
        self.parser.add_argument('owner_id', type=int, required=True)

    def get(self, recipe_id):
        abort_if_recipe_not_found()
        session = db_session.create_session()
        recipe = session.query(Recipes).get(recipe_id)
        return jsonify({'job': recipe.to_dict(
            only=('name', 'content', 'products', 'cost', 'owner_id'))})