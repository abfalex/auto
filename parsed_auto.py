import time
import json
import os
from os.path import join

import requests
from pathvalidate import sanitize_filename
from bs4 import BeautifulSoup


BRAND_COUNT = 6
FILENAME = 'brands.json'
FOLDER = ''


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError


def get_response(url):
    while True:
        try:
            response = requests.get(url)
            response.raise_for_status()
            check_for_redirect(response)
            break
        except requests.exceptions.ConnectionError:
            print('Ошибка подключения')
            time.sleep(5)
    return response


def save_brands_json(brands, folder=FOLDER):
    if folder:
        os.makedirs(folder, exist_ok=True)
    filepath = join(folder, sanitize_filename(FILENAME))
    with open(filepath, 'w', encoding='utf8') as file:
        json.dump(brands, file)


def find_cars_brand(soup):
    brands = {}
    soups = soup.select('[class="css-m7q1zs e4ojbx42"]')
    for soup in soups[:BRAND_COUNT]:
        image_url = soup.find('img')['src']
        brand_name = soup.find('a').text
        brands[brand_name] = image_url
    return brands


def parse_car_brand():
    url = 'https://auto.drom.ru/'
    try:
        response = get_response(url)
    except requests.exceptions.HTTPError:
        print(f'Не существует такой ссылки - {response.url}')
    soup = BeautifulSoup(response.content, 'lxml')
    return find_cars_brand(soup)

def main():
    brands = parse_car_brand()
    save_brands_json(brands)


if __name__ == '__main__':
    main()
