from flask import jsonify
from flask_restful import Resource, reqparse

from data import db_session
from data.users import User
from data.resources import abort_if_user_not_found


class UsersResource(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('surname', required=True)
        self.parser.add_argument('name', required=True)
        self.parser.add_argument('age', required=True, type=int)
        self.parser.add_argument('position', required=True)
        self.parser.add_argument('speciality', required=True)
        self.parser.add_argument('address', required=True)
        self.parser.add_argument('email', required=True)
        self.parser.add_argument('password', required=True)

    def get(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        users = session.query(User).get(user_id)
        return jsonify({'news': users.to_dict(
            only=('name', 'surname', 'age', 'email'))})

    def patch(self, users_id):
        abort_if_user_not_found(users_id)
        session = db_session.create_session()
        user = session.query(User).get(users_id)
        args = self.parser.parse_args()

        user.surname = args['surname']
        user.name = args['name']
        user.age = args['age']
        user.email = args['email']
        user.position = args['position']
        user.speciality = args['speciality']
        user.address = args['address']

        session.commit()

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
        self.parser.add_argument('surname', required=True)
        self.parser.add_argument('name', required=True)
        self.parser.add_argument('age', required=True, type=int)
        self.parser.add_argument('position', required=True)
        self.parser.add_argument('speciality', required=True)
        self.parser.add_argument('address', required=True)
        self.parser.add_argument('email', required=True)
        self.parser.add_argument('password', required=True)

    def get(self):
        session = db_session.create_session()
        users = session.query(User).all()
        return jsonify({'users': [item.to_dict(
            only=('name', 'surname', 'age', 'email')) for item in users]})

    def post(self):
        args = self.parser.parse_args()
        session = db_session.create_session()
        user = User(
            name=args['name'],
            surname=args['surname'],
            age=args['age'],
            email=args['email'],
            address=args['address'],
            speciality=args['speciality'],
            position=args['position']
        )

        user.set_password(args['password'])
        session.add(user)
        session.commit()
        return jsonify({'success': 'OK'})
