from requests import get, post, delete

print(get('http://localhost:5000/api/v2/users').json())  # correct
print(get('http://localhost:5000/api/v2/users/1').json())  # correct
print(delete('http://localhost:5000/api/v2/users/2').json())  # bad id

print(delete('http://localhost:5000/api/v2/users/200000').json())  # bad id
print(delete('http://localhost:5000/api/v2/users/2001200').json())  # bad id
print(get('http://localhost:5000/api/v2/users/1212121212').json())  # bad id

print(post('http://localhost:5000/api/v2/users',
           json={'surname': 'bib',
                 'name': 'bob',
                 'age': 12,
                 'address': 'bub',
                 'speciality': 'mim',
                 'position': 'nigga',
                 'email': 'bob@mail.ru'}).json())  # correct
