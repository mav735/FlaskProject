from requests import get, post, delete

print(get('http://localhost:5000/api/v2/jobs').json())  # correct
print(get('http://localhost:5000/api/v2/jobs/2').json())  # correct
print(delete('http://localhost:5000/api/v2/jobs/3').json())  # correct

print(delete('http://localhost:5000/api/v2/jobs/200000').json())  # bad id
print(delete('http://localhost:5000/api/v2/jobs/2001200').json())  # bad id
print(get('http://localhost:5000/api/v2/jobs/1212121212').json())  # bad id

print(post('http://localhost:5000/api/v2/jobs',
           json={'job': 'bib',
                 'work_size': 123,
                 'collaborators': '1, 2, 3',
                 'is_finished': "False",
                 'team_leader': 1}).json())  # correct
