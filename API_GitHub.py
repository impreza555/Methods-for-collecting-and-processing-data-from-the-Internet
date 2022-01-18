import os
from dotenv import load_dotenv
import requests
import json


load_dotenv()
username = os.environ.get('USER_NAME')
token = os.environ.get('GITHUB_TOKEN')
repos = requests.get('https://api.github.com/user/repos', auth=(username, token))
with open("api_github.json", "w") as file:
    json.dump(repos.json(), file, sort_keys=True, ensure_ascii=False, indent=4)
for repo in repos.json():
    print(f'Название репозитория: {repo["name"]}')
    print(f'URL репозитория: {repo["html_url"]}')
