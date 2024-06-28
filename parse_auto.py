import time
import json
import os
import argparse
from os.path import split
from os.path import join
from urllib.parse import urlsplit
from urllib.parse import unquote

import requests
from pathvalidate import sanitize_filename
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()


BRANDS_FILENAME = os.getenv('BRANDS_FILENAME', default='brands.json')
BRANDS_FOLDER = os.getenv('BRANDS_FOLDER', default='brands\\')
CAR_IMG_FOLDER = os.getenv('CAR_IMG_FOLDER', default='media\\')
PAGE_COUNT = os.getenv('PAGE_COUNT')
BRAND_NAMES = os.getenv('BRAND_NAMES')


def get_arg():
    parser = argparse.ArgumentParser()
    parser.add_argument('--page_count', type=int, default=3,
                        help='Количество страниц с авто, у одного бренда.')
    return parser.parse_args()


def get_page_count():
    if os.getenv('PAGE_COUNT'):
        return os.getenv('PAGE_COUNT')
    return get_arg().page_count


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError


def find_mileage(soup):
    try:
        text = soup.select('[class="css-1l9tp44 e162wx9x0"]')[-1].text
        if text[-2:] != 'км':
            return None
        text = text[:-3]
        text = int(text.replace(' ', ''))
        return text
    except ValueError:
        return None


def find_engine(soup):
    try:
        capacity, fuel = find_capacity(soup), find_fuel(soup)
        if fuel == 'электро':
            capacity = None
        engine = {
            'capacity': capacity,
            'fuel': fuel
        }
        return engine
    except IndexError:
        return None


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
    try:
        text = soup.select('[class="css-1l9tp44 e162wx9x0"]')[3].text
        if text[-1] == ',':
            text = text[:-1]
        if text not in ['задний', '4WD', 'передний']:
            return None
        return text
    except IndexError:
        return None


def find_transmission(soup):
    try:
        text = soup.select('[class="css-1l9tp44 e162wx9x0"]')[2].text
        if text[-1] == ',':
            return soup.select('[class="css-1l9tp44 e162wx9x0"]')[2].text[:-1]
        if text not in ['АКПП', 'автомат', 'механика', 'робот', 'вариатор']:
            return None
        return text
    except IndexError:
        return None


def find_power(soup):
    try:
        text = soup.select_one('[class="css-1l9tp44 e162wx9x0"]').text
        text = text.encode('unicode_escape').decode('unicode_escape')
        text = text[text.find('(') + 1:text.find(')')]
        return int(text[:-5])
    except ValueError:
        return None
    except AttributeError:
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
    if not text:
        return None
    return text.find('img')['src']


def find_model(soup):
    try:
        text = soup.select_one('[class="css-16kqa8y e3f4v4l2"]').text
        return text.split(',')[0]
    except AttributeError:
        return None


def make_url(page, brand):
    url = f'https://auto.drom.ru/{brand}/all/page{page}/?'
    if page == 1:
        url = f'https://auto.drom.ru/{brand}/all/?'
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
        'drom_url': soup['href'],
        'img_path': None
    }
    return car


def parse_brand_cars(brand, page_count, folder):
    """Возвращает список автомобилей определенного бренда"""
    cars = []
    params = {'ph': 1, 'unsold': 1}
    for page in range(1, int(page_count)+1):
        try:
            url = make_url(page, brand)
            response = get_response(url, params=params)
            soup = BeautifulSoup(response.content, 'lxml')
            cars = cars + find_cars(soup)
        except requests.exceptions.HTTPError:
            print(f'Не существует такой ссылки - {url}')
    return download_car_images(cars, brand, folder)


def download_car_images(cars, brand, folder):
    result_folder = join(folder, brand)
    for car in cars:
        url_path = urlsplit(car['img_url']).path
        filename = unquote(split(url_path)[-1])
        car['img_path'] = download_image(car['img_url'],
                                         filename,
                                         result_folder
                                         )
    return cars


def find_cars(page_soup):
    cars = []
    cards = page_soup.select('[class="css-4zflqt e1huvdhj1"]')
    for card in cards:
        cars.append(get_car(card))
    return cars


def get_response(url, params={}):
    while True:
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            check_for_redirect(response)
            return response
        except requests.exceptions.ConnectionError:
            print('Ошибка подключения')
            time.sleep(5)


def correct_json_filename(filename):
    if filename[-5:] != '.json':
        filename = filename + '.json'
    return sanitize_filename(filename)


def save_json(brands, filename, folder=''):
    if folder:
        os.makedirs(folder, exist_ok=True)
    filepath = join(folder, correct_json_filename(filename))
    with open(filepath, 'w', encoding='utf8') as file:
        json.dump(brands, file, ensure_ascii=False)


def save_image(content, filename, folder=''):
    if folder:
        os.makedirs(folder, exist_ok=True)
    filepath = join(folder, sanitize_filename(filename))
    with open(filepath, 'wb') as file:
        file.write(content)
    return filepath


def download_image(url, filename, folder=''):
    """Скачивает изображение и сохраняет по указанному пути"""
    try:
        response = get_response(url)
        return save_image(response.content, filename, folder)
    except requests.exceptions.HTTPError:
        print(f'Не существует такой ссылки - {url}')
        return None


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
                'image_url': image_url,
                'image_path': None
            }
            brands.append(brand)
    return brands


def parse_car_brands(brand_names, folder):
    """Возвращает данные указанных брендов в виде списка"""
    url = 'https://auto.drom.ru/'
    try:
        response = get_response(url)
        soup = BeautifulSoup(response.content, 'lxml')
        brands = find_car_brands(soup, brand_names)
        return download_brand_images(brands, folder)
    except requests.exceptions.HTTPError:
        print(f'Не существует такой ссылки - {url}')


def get_brand_names():
    if BRAND_NAMES:
        return BRAND_NAMES.split(',')
    return ['bmw', 'lexus', 'ford', 'mazda', 'chevrolet', 'mercedes-benz']


def download_brand_images(brands, folder):
    for brand in brands:
        result_folder = join(folder, brand['brand_name'].lower())
        url_path = urlsplit(brand['image_url']).path
        filename = unquote(split(url_path)[-1])
        brand['image_path'] = download_image(brand['image_url'],
                                             filename,
                                             result_folder
                                             )
    return brands


def main():
    page_count = get_page_count()
    brand_names = get_brand_names()
    brands = parse_car_brands(brand_names, CAR_IMG_FOLDER)
    save_json(brands, BRANDS_FILENAME, BRANDS_FOLDER)
    for brand in brand_names:
        cars = parse_brand_cars(brand, page_count, CAR_IMG_FOLDER)
        save_json(cars, f'{brand}_cars', join(BRANDS_FOLDER, brand))


if __name__ == '__main__':
    main()
