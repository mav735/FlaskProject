from flask import jsonify
from flask_restful import Resource, reqparse

from data import db_session
from data.products import Products
from data.recipes import Recipes
from data.resources import abort_if_recipe_not_found


class RecipesResource(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('name', required=True)
        self.parser.add_argument('content', required=True)
        self.parser.add_argument('products', required=True)
        self.parser.add_argument('image', required=True)
        self.parser.add_argument('caloric', type=int, required=True)
        self.parser.add_argument('owner_id', type=int, required=True)

    def delete(self, recipe_id):
        abort_if_recipe_not_found(recipe_id)
        session = db_session.create_session()
        recipe = session.query(Recipes).get(recipe_id)
        session.delete(recipe)
        session.commit()
        return jsonify({'success': 'OK'})

    def patch(self, recipe_id):
        abort_if_recipe_not_found(recipe_id)
        session = db_session.create_session()
        recipe = session.query(Recipes).get(recipe_id)
        args = self.parser.parse_args()
        print(args)

        products = args['products'].split(', ')
        recipe_cost = 0
        for element in products:
            now = session.query(Products).get(int(element))
            if now is not None:
                recipe_cost += now.cost

        recipe.name = args['name']
        recipe.content = args['content']
        recipe.products = args['products']
        recipe.owner_id = int(args['owner_id'])
        recipe.caloric_content = int(args['caloric'])
        recipe.cost = int(recipe_cost)
        recipe.image = args['image']

        session.commit()

        return jsonify({'success': 'OK'})

    def get(self, recipe_id):
        abort_if_recipe_not_found(recipe_id)
        session = db_session.create_session()
        recipe = session.query(Recipes).get(recipe_id)
        return jsonify({'recipe': recipe.to_dict(
            only=('name', 'content', 'products', 'cost', 'owner_id', 'image', 'caloric_content'))})


class RecipesListResource(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('name', required=True)
        self.parser.add_argument('content', required=True)
        self.parser.add_argument('products', required=True)
        self.parser.add_argument('image', required=True)
        self.parser.add_argument('caloric', type=int, required=True)
        self.parser.add_argument('owner_id', type=int, required=True)

    def post(self):
        args = self.parser.parse_args()
        session = db_session.create_session()
        products = args['products'].split(', ')
        recipe_cost = 0
        for element in products:
            now = session.query(Products).get(int(element))
            if now is not None:
                recipe_cost += now.cost

        recipe = Recipes(
            name=args['name'],
            content=args['content'],
            products=args['products'],
            owner_id=int(args['owner_id']),
            caloric_content=int(args['caloric']),
            cost=int(recipe_cost),
            image=args['image']
        )

        session.add(recipe)
        session.commit()
