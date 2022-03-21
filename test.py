import json

data = {'job': 'АбобаApi',
        'work_size': 10020,
        'collaborators': '1, 2, 3',
        'team_leader': 1,
        'is_finished': 1}

with open('data.txt', 'w', encoding='utf-8') as outfile:
    json.dump(data, outfile, sort_keys=True, indent=4,
              ensure_ascii=False)
