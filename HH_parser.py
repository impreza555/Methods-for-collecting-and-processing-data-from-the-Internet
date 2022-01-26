import csv

import requests
from bs4 import BeautifulSoup


def parser(keyword):
    vacancy_list = []
    url = 'https://hh.ru'
    params = {
        'area': '113',
        'search_field': ['name', 'company_name', 'description'],
        'text': keyword,
        'page': '0',
        'items_on_page': '20'
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36 OPR/83.0.4254.19'
    }
    response = requests.get(url + '/search/vacancy', params=params, headers=headers)
    dom = BeautifulSoup(response.text, 'html.parser')
    last_pg = int(dom.find('a', {'data-qa': 'pager-next'}).previous_sibling.find('a', {'class': 'bloko-button'}).find(
        'span').getText())
    for pg in range(0, last_pg + 1):
        params['page'] = str(pg)
        response = requests.get(url + '/search/vacancy', params=params, headers=headers)
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
                currency_of_salary = salary[2]
            elif salary[0] == 'до':
                salary_min = None
                salary_max = int(salary[1])
                currency_of_salary = salary[2]
            else:
                salary_min = int(salary[0])
                salary_max = int(salary[1])
                currency_of_salary = salary[2]
            vacancy_dict['название_вакансии'] = vacancy_title
            vacancy_dict['ссылка_на_вакансию'] = vacancy_link
            vacancy_dict['мин_зарплата'] = salary_min
            vacancy_dict['макс_зарплата'] = salary_max
            vacancy_dict['валюта_зарплаты'] = currency_of_salary
            vacancy_dict['сайт_поиска'] = url
            vacancy_list.append(vacancy_dict)
    with open('HH_vacancy.csv', 'w', encoding='utf-8') as f:
        writer = csv.DictWriter(
            f, fieldnames=list(vacancy_list[0].keys()), lineterminator='\r', delimiter=",", quotechar='"')
        writer.writeheader()
        for _ in vacancy_list:
            writer.writerow(_)


if __name__ == "__main__":
    text = input('Введите название профессии: ')
    # text = 'python django'
    parser(text)
