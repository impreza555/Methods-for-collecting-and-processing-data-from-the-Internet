from pprint import pprint

from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client['vacancies']
HH_vacancies = db.HH_vacancies


def salary_search(sum, curr):
    for vacancy in HH_vacancies.find({'$and': [{'currency_of_salary': curr}, {
        '$or': [{'$and': [{'salary_min': {'$eq': None}, 'salary_max': {'$gte': sum}}]},
                {'$and': [{'salary_min': {'$gt': sum}, 'salary_max': {'$eq': None}}]},
                {'$and': [{'salary_min': {'$gt': sum}, 'salary_max': {'$gte': sum}}]}]}]}):
        pprint(vacancy)


if __name__ == "__main__":
    summa_babok = int(input('Введите желаемую сумму зарплаты: '))
    currency = input('Введите валюту (RUB, USD или EUR): ').upper()
    if currency != 'RUB' or currency != 'USD' or currency != 'EUR':
        currency = 'RUB'
    # currency = 'RUB'
    # summa_babok = 60000
    salary_search(summa_babok, currency)
