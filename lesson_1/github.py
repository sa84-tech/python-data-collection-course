import requests
import json

URL = 'https://api.github.com/users/'

USER_NAME = input('Enter github account name: ')  # for example: defunkt

response = requests.get(f'{URL}{USER_NAME}/repos')

if response.ok:
    repos_data = json.loads(response.text)
    print(f'List of public repositories for GitHub account {USER_NAME}:')
    for repo in repos_data:
        print(f"{repo['name']} - {repo['url']}")
    with open('repos.json', 'w', encoding='utf-8') as f_n:
        f_n.write(json.dumps(repos_data))
else:
    print(f'Error: status_code: {response.status_code}')
