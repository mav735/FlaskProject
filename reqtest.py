from requests import get, put

print(put('http://localhost:5000/api/jobs/2', json={
    "collaborators": "1, 2",
    "is_finished": 0,
    "job": "АбобаApi123",
    "team_leader": 1,
    "work_size": 10020
}).json())  # normal request

print(put('http://localhost:5000/api/jobs/999', json={
    "collaborators": "1, 2",
    "is_finished": 0,
    "job": "АбобаApi123",
    "team_leader": 1,
    "work_size": 10020
}).json())  # Bad id request

print(get('http://localhost:5000/api/jobs').json())
