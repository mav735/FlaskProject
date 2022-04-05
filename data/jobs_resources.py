import datetime

from flask import jsonify
from flask_restful import Resource, reqparse

from data import db_session
from data.jobs import Jobs
from data.resources import abort_if_job_not_found


class JobsResource(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('job', required=True)
        self.parser.add_argument('work_size', type=int, required=True)
        self.parser.add_argument('collaborators', required=True)
        self.parser.add_argument('is_finished', type=bool, required=True)
        self.parser.add_argument('team_leader', type=int, required=True)

    def get(self, job_id):
        abort_if_job_not_found(job_id)
        session = db_session.create_session()
        job = session.query(Jobs).get(job_id)
        print(job_id, job, sep='\n')
        return jsonify({'job': job.to_dict(
            only=('job', 'work_size', 'collaborators', 'is_finished', 'team_leader'))})

    def patch(self, job_id):
        abort_if_job_not_found(job_id)
        session = db_session.create_session()
        job = session.query(Jobs).get(job_id)
        args = self.parser.parse_args()

        job.job = args['job']
        job.work_size = args['work_size']
        job.collaborators = args['collaborators']
        job.is_finished = args['is_finished']
        job.team_leader = args['team_leader']

        session.commit()

    def delete(self, job_id):
        abort_if_job_not_found(job_id)
        session = db_session.create_session()
        job = session.query(Jobs).get(job_id)

        session.delete(job)
        session.commit()

        return jsonify({'success': 'OK'})


class JobsListResource(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('job', required=True)
        self.parser.add_argument('work_size', required=True)
        self.parser.add_argument('collaborators', required=True)
        self.parser.add_argument('is_finished', required=True)
        self.parser.add_argument('team_leader', required=True)

    def get(self):
        session = db_session.create_session()
        users = session.query(Jobs).all()
        return jsonify({'jobs': [item.to_dict(
            only=('job', 'work_size', 'collaborators', 'is_finished', 'team_leader', 'id')) for item in users]})

    def post(self):
        args = self.parser.parse_args()
        session = db_session.create_session()
        job = Jobs(
            job=args['job'],
            work_size=args['work_size'],
            collaborators=args['collaborators'],
            is_finished=bool(args['is_finished']),
            team_leader=args['team_leader'],
            start_date=datetime.datetime.now(),
            end_date=datetime.datetime.now()
        )
        session.add(job)
        session.commit()
        return jsonify({'success': 'OK'})
