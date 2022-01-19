import requests
import json


username = 'USER_NAME' #'impreza555'
repos = requests.get(f'https://api.github.com/users/{username}/repos')
with open("api_github.json", "w") as file:
    json.dump(repos.json(), file, sort_keys=True, ensure_ascii=False, indent=4)
for repo in repos.json():
    print(f'Название репозитория: {repo["name"]}')
    print(f'URL репозитория: {repo["html_url"]}')
