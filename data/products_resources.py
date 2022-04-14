from flask import jsonify
from flask_restful import Resource, reqparse

from data import db_session
from data.products import Products
from data.resources import abort_if_products_not_found


class ProductsResource(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('name', required=True)
        self.parser.add_argument('cost', required=True)

    def get(self, product_id):
        abort_if_products_not_found(product_id)
        session = db_session.create_session()
        products = session.query(Products).get(product_id)
        return jsonify({'product': products.to_dict(only=('name', 'cost', 'id'))})

    def patch(self, product_id):
        abort_if_products_not_found(product_id)
        session = db_session.create_session()
        product = session.query(Products).get(product_id)

        args = self.parser.parse_args()

        product.name = args['name']
        product.cost = args['cost']
        session.commit()
        return jsonify({'success': 'OK'})

    def delete(self, product_id):
        abort_if_products_not_found(product_id)
        session = db_session.create_session()

        product = session.query(Products).get(product_id)
        session.delete(product)
        session.commit()
        return jsonify({'success': 'OK'})


class ProductsListResource(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('name', required=True)
        self.parser.add_argument('cost', required=True)

    def get(self):
        session = db_session.create_session()
        products = session.query(Products).all()
        return jsonify({'products': [item.to_dict(
            only=('name', 'cost', 'id')) for item in products]})

    def post(self):
        args = self.parser.parse_args()
        session = db_session.create_session()

        product = Products(
            name=args['name'],
            cost=args['cost']
        )

        session.add(product)
        session.commit()

        return jsonify({'success': 'OK'})
