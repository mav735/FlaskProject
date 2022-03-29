from flask import jsonify
from flask_restful import Resource, reqparse

from data import db_session
from data.news import News
from data.resources import abort_if_news_not_found


class NewsResource(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('title', required=True)
        self.parser.add_argument('content', required=True)
        self.parser.add_argument('is_private', required=True, type=bool)

    def get(self, news_id):
        abort_if_news_not_found(news_id)
        session = db_session.create_session()
        news = session.query(News).get(news_id)
        return jsonify({'news': news.to_dict(
            only=('title', 'content', 'user_id', 'is_private'))})

    def patch(self, news_id):
        abort_if_news_not_found(news_id)
        session = db_session.create_session()
        news = session.query(News).get(news_id)
        args = self.parser.parse_args()
        news.title = args['title']
        news.content = args['content']
        news.is_private = args['is_private']
        session.commit()

    def delete(self, news_id):
        abort_if_news_not_found(news_id)
        session = db_session.create_session()
        news = session.query(News).get(news_id)
        session.delete(news)
        session.commit()
        return jsonify({'success': 'OK'})


class NewsListResource(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('title', required=True)
        self.parser.add_argument('content', required=True)
        self.parser.add_argument('is_private', required=True, type=bool)
        self.parser.add_argument('user_id', required=True, type=int)

    def get(self):
        session = db_session.create_session()
        news = session.query(News).all()
        return jsonify({'news': [item.to_dict(
            only=('title', 'content', 'user.name')) for item in news]})

    def post(self):
        args = self.parser.parse_args()
        session = db_session.create_session()
        news = News(
            title=args['title'],
            content=args['content'],
            user_id=args['user_id'],
            is_private=args['is_private']
        )
        session.add(news)
        session.commit()
        return jsonify({'success': 'OK'})
