import time
import json
import os
from os.path import join
from pprint import pprint

import requests
from pathvalidate import sanitize_filename
from bs4 import BeautifulSoup

 
FILENAME = 'brands.json'
BRAND_NAMES = ['bmw', 'lexus', 'ford', 'mazda', 'chevrolet', 'mercedes-benz']
FOLDER = ''


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError


def find_mileage(soup):
    try:
        text = soup.select('[class="css-1l9tp44 e162wx9x0"]')[-1].text
        text = text[:-3]
        text = int(text.replace(' ', ''))
        return text
    except ValueError:
        return None


def find_engine(soup):
    engine = {
        'capacity': find_capacity(soup),
        'fuel': find_fuel(soup)
    }
    return engine


def find_fuel(soup):
    text = soup.select('[class="css-1l9tp44 e162wx9x0"]')[1].text
    if text[-1] == ',':
        return soup.select('[class="css-1l9tp44 e162wx9x0"]')[1].text[:-1]
    return text


def find_capacity(soup):
    try:
        text = soup.select_one('[class="css-1l9tp44 e162wx9x0"]').text
        text = text.encode('unicode_escape').decode('unicode_escape')
        return float(text.split()[0])
    except ValueError:
        return None


def find_wheel_drive(soup):
    text = soup.select('[class="css-1l9tp44 e162wx9x0"]')[3].text
    if text[-1] == ',':
        return soup.select('[class="css-1l9tp44 e162wx9x0"]')[3].text[:-1]
    return text


def find_transmission(soup):
    text = soup.select('[class="css-1l9tp44 e162wx9x0"]')[2].text
    if text[-1] == ',':
        return soup.select('[class="css-1l9tp44 e162wx9x0"]')[2].text[:-1]
    return text


def find_power(soup):
    try:
        text = soup.select_one('[class="css-1l9tp44 e162wx9x0"]').text
        text = text.encode('unicode_escape').decode('unicode_escape')
        text = text[text.find('(') + 1:text.find(')')]
        return int(text[:-5])
    except ValueError:
        return None


def find_year(soup):
    try:
        text = soup.select_one('[class="css-16kqa8y e3f4v4l2"]').text
        return int(text.split(',')[1])
    except ValueError:
        return None


def find_price(soup):
    try:
        text = soup.select_one('[data-ftid="bull_price"]').text
        text = text.encode('unicode_escape').decode().replace('\\xa0', '')
        return int(text)
    except ValueError:
        return None


def find_img_url(soup):
    text = soup.select_one('[class="css-1jfqfiu e1e9ee560"]')
    return text.find('img')['src']


def find_model(soup):
    text = soup.select_one('[class="css-16kqa8y e3f4v4l2"]').text
    return text.split(',')[0]


def make_url(page, brand):
    url = f'https://auto.drom.ru/{brand}/all/page{page}/?ph=1&unsold=1'
    if page == 1:
        url = f'https://auto.drom.ru/{brand}/all/?ph=1&unsold=1'
    return url


def get_car(soup):
    car = {
        'model': find_model(soup),
        'img_url': find_img_url(soup),
        'price': find_price(soup),
        'year': find_year(soup),
        'power': find_power(soup),
        'transmission': find_transmission(soup),
        'wheel_drive': find_wheel_drive(soup),
        'engine': find_engine(soup),
        'mileage': find_mileage(soup),
        'drom_url': soup['href']
    }
    return car


def parse_brand_cars(brand, page_count):
    cars = []
    for page in range(1, page_count+1):
        try:
            url = make_url(page, brand)
            response = get_response(url)
            soup = BeautifulSoup(response.content, 'lxml')
            cars = cars + find_cars(soup)
        except requests.exceptions.HTTPError:
            print('Не существует такой ссылки')
    return cars


def find_cars(page_soup):
    cars = []
    cards = page_soup.select('[class="css-4zflqt e1huvdhj1"]')
    for card in cards:
        cars.append(get_car(card))
    return cars


def get_response(url):
    while True:
        try:
            response = requests.get(url)
            response.raise_for_status()
            check_for_redirect(response)
            return response
        except requests.exceptions.ConnectionError:
            print('Ошибка подключения')
            time.sleep(5)


def save_brands_json(brands, filename=FILENAME, folder=FOLDER):
    if folder:
        os.makedirs(folder, exist_ok=True)
    filepath = join(folder, sanitize_filename(filename))
    with open(filepath, 'w', encoding='utf8') as file:
        json.dump(brands, file)


def lower_list(data):
    data = map(lambda x: x.lower(), data)
    return (list(data))


def find_car_brands(soup, brand_names):
    brands = []
    soups = soup.select('[class="css-m7q1zs e4ojbx42"]')
    for soup in soups:
        image_url = soup.find('img')['src']
        brand_name = soup.find('a').text
        if brand_name.lower() in lower_list(brand_names):
            brand = {
                'brand_name': brand_name,
                'image_url': image_url
            }
            brands.append(brand)
    return brands


def parse_car_brands(brand_names):
    url = 'https://auto.drom.ru/'
    try:
        response = get_response(url)
        soup = BeautifulSoup(response.content, 'lxml')
        return find_car_brands(soup, brand_names)
    except requests.exceptions.HTTPError:
        print('Не существует такой ссылки.')


def main():
    brands = parse_car_brands()
    save_brands_json(brands)


<<<<<<< Updated upstream
if __name__ == '__main__':
    # for brand in ['audi', 'bmw', 'chery', ]
    # pprint(parse_brand_cars('bmw', 3))
    save_brands_json(parse_car_brands(BRAND_NAMES))
