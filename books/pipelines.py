from pymongo import MongoClient


class BooksPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongobase = client.books

    def process_item(self, item, spider):
        book = self.clear_items(item.get('book_title'), item.get('price_base'), item.get('price_discount'),
                                item.get('book_rating'))
        item['book_title'], item['price_base'], item['price_discount'], item['book_rating'] = book
        collection = self.mongobase[spider.name]
        collection.update_one({'link_to_book': item['link_to_book']}, {'$set': item}, upsert=True)
        return item

    @staticmethod
    def clear_items(book_title, price_base, price_discount, book_rating):
        book_title = book_title.lstrip().rstrip()
        if price_base is not None:
            price_base = int(price_base.replace('\xa0', '').replace(' ', '').replace('₽', ''))
        if price_discount is not None:
            price_discount = int(price_discount.replace('\xa0', '').replace(' ', '').replace('₽', ''))
        if book_rating is not None:
            book_rating = float(book_rating.lstrip().rstrip().replace(',', '.'))
            return book_title, price_base, price_discount, book_rating
