from pymongo import MongoClient
from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.options import Options

client = MongoClient('localhost', 27017)
mongo_base = client['mvideo']
collection = mongo_base['in_trend']

edge_options = Options()
edge_options.add_argument("start-maximized")
driver = webdriver.Edge(executable_path='./msedgedriver', options=edge_options)
driver.implicitly_wait(10)
driver.get('https://www.mvideo.ru/')
assert 'М.Видео' in driver.title
lebel = driver.find_element(By.XPATH, "//a[@class='logo ng-tns-c279-2 ng-star-inserted'][@title='Главная']")
while True:
    try:
        elem = driver.find_element(By.XPATH, "//button[@class='tab-button ng-star-inserted']//span[@class='title']")
        break
    except exceptions.NoSuchElementException:
        lebel.send_keys(Keys.PAGE_DOWN)
elem.click()
products = driver.find_elements(By.XPATH,
                                '//mvid-carousel[@class="carusel ng-star-inserted"]//mvid-product-cards-group//div[contains(@class, "product-mini-card__image")]//a')
links = []
for _ in products:
    link = _.get_attribute('href')
    links.append(link)
for link in links:
    product = {}
    product['link'] = link
    driver.implicitly_wait(10)
    driver.get(link)
    product['name'] = driver.find_element(By.XPATH, '//h1').get_attribute('innerHTML')
    product['price'] = driver.find_element(By.XPATH,
                                           '//mvideoru-product-details-card//span[@class="price__main-value"]').get_attribute(
        'innerHTML').replace('&nbsp', '').replace(';', '').replace('₽', '')
    try:
        product['image'] = driver.find_element(By.XPATH,
                                               '//div[contains(@class, "zoomable-image")]').value_of_css_property(
            "background-image").replace('url(', '').replace(')', '').replace('"', '')
    except exceptions.NoSuchElementException:
        product['image'] = driver.find_element(By.XPATH, '//img[contains(@class, "zoomable-image")]').get_attribute(
            'src')
    collection.update_one({'link': product['link']}, {'$set': product}, upsert=True)

driver.quit()
