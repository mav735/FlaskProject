from flask import jsonify
from flask_restful import Resource, reqparse

from data import db_session
from data.users import User
from data.resources import abort_if_user_not_found


class UsersResource(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('login', required=True)
        self.parser.add_argument('password', required=True)
        self.parser.add_argument('email', required=True)

    def get(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        users = session.query(User).get(user_id)
        return jsonify({'user': users.to_dict(only=('login', 'email', 'favourite_recipes_ids',
                                                    'owned_recipes_ids', 'orders_ids'))})

    def patch(self, user_id):
        abort_if_user_not_found(user_id)

        session = db_session.create_session()
        user = session.query(User).get(user_id)
        args = self.parser.parse_args()

        user.email = args['email']
        user.set_password(args['password'])

        session.commit()

        return jsonify({'success': 'OK'})

    def delete(self, user_id):
        abort_if_user_not_found(user_id)

        session = db_session.create_session()
        user = session.query(User).get(user_id)

        session.delete(user)
        session.commit()

        return jsonify({'success': 'OK'})


class UsersListResource(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('login', required=True)
        self.parser.add_argument('password', required=True)
        self.parser.add_argument('email', required=True)

    def get(self):
        session = db_session.create_session()
        users = session.query(User).all()
        return jsonify({'users': [item.to_dict(
            only=('login', 'email', 'favourite_recipes_ids',
                  'owned_recipes_ids', 'orders_ids')) for item in users]})

    def post(self):
        args = self.parser.parse_args()
        session = db_session.create_session()
        user = User(
            login=args['login'],
            email=args['email'])

        user.set_password(args['password'])
        session.add(user)
        session.commit()
        return jsonify({'success': 'OK'})
