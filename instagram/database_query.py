from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client['instagram_scrapy']
users = db.instagram

name = input('Укажите имя пользователя: ')
cnt = users.count_documents({'$and': [{'source_name': name, 'subs_type': 'subscriber'}]})
print(f'Подписчики {cnt}:')
print('-' * 50)
for user in users.find({'$and': [{'source_name': name, 'subs_type': 'subscriber'}]}):
    print(user.get('user_name'))
print('*' * 50)
cnt = users.count_documents({'$and': [{'source_name': name, 'subs_type': 'subscription'}]})
print(f'Подписки {cnt}:')
print('-' * 50)
for user in users.find({'$and': [{'source_name': name, 'subs_type': 'subscription'}]}):
    print(user.get('user_name'))
