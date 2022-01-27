import hashlib

import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from pymongo import errors
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

client = MongoClient('localhost', 27017)
db = client['vacancies']
HH_vacancies = db.HH_vacancies


def parser(keyword):
    url = 'https://hh.ru'
    params = {
        'area': '113',
        'search_field': ['name', 'company_name', 'description'],
        'text': keyword,
        'order_by': 'relevance',
        'page': '0',
        'items_on_page': '20'
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36 OPR/83.0.4254.19'
    }
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    response = session.get(url + '/search/vacancy', params=params, headers=headers)
    dom = BeautifulSoup(response.text, 'html.parser')
    last_pg = int(dom.find('a', {'data-qa': 'pager-next'}).previous_sibling.find('a', {'class': 'bloko-button'}).find(
        'span').getText())
    for pg in range(0, last_pg + 1):
        params['page'] = str(pg)
        response = session.get(url + '/search/vacancy', params=params, headers=headers)
        dom = BeautifulSoup(response.text, 'html.parser')
        vacancy_data = dom.find_all('div', {'class': 'vacancy-serp-item'})
        for vacancy in vacancy_data:
            vacancy_dict = {}
            vacancy_title = vacancy.find('a', {'class': 'bloko-link'}).getText()
            vacancy_link = vacancy.find('a', {'class': 'bloko-link'})['href']
            try:
                salary = vacancy.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'}).getText().replace(
                    '\u202f', '').replace('–', '').split()
            except:
                salary = None
            if not salary:
                salary_min = None
                salary_max = None
                currency_of_salary = None
            elif salary[0] == 'от':
                salary_min = int(salary[1])
                salary_max = None
                currency_of_salary = salary[2].replace('руб.', 'RUB')
            elif salary[0] == 'до':
                salary_min = None
                salary_max = int(salary[1])
                currency_of_salary = salary[2].replace('руб.', 'RUB')
            else:
                salary_min = int(salary[0])
                salary_max = int(salary[1])
                currency_of_salary = salary[2].replace('руб.', 'RUB')
            vacancy_dict['vacancy_title'] = vacancy_title
            vacancy_dict['vacancy_link'] = vacancy_link
            vacancy_dict['salary_min'] = salary_min
            vacancy_dict['salary_max'] = salary_max
            vacancy_dict['currency_of_salary'] = currency_of_salary
            vacancy_dict['search_site'] = url
            id = hashlib.md5(str(vacancy_dict).encode('utf-8')).hexdigest()
            vacancy_dict['_id'] = id
            try:
                HH_vacancies.insert_one(vacancy_dict)
            except errors.DuplicateKeyError:
                print(f'Вакансия {vacancy_dict["vacancy_title"]} уже существует в базе')
                continue


if __name__ == "__main__":
    text = input('Введите название профессии: ')
    # text = 'python django'
    parser(text)
