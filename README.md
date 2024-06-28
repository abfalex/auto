# auto
Сайт с объявлениями о продаже автомобилей разных марок.
На сайт попадают авто только с фотографиями.
Данные берутся с сайта `drom.ru`.

## Как запустить оффлайн сайт в браузере?
Для запуска сайта вам понадобится Python третьей версии.
Скачайте код с GitHub. Затем используйте pip (или pip3, есть конфликт с Python2) для установки зависимостей:
```sh
pip install -r requirements.txt
```
Все необходимые данные для оффлайн работы сайта, уже имеются в репозитории.
Запустите сайт при помощи команды:
```sh
python render_website.py
```
Затем откройте в браузере сайт, он будет доступен по [ссылке](http://127.0.0.1:5500) - `http://127.0.0.1:5500`.

В корне репозитория будет создана папка `pages` со страницами автомобилей, рассортированная по брендам, а также файл `index.html`, который является главной страницой сайта.
## Как спарсить данные для сайта?
Все настройки для парсинга имеют дефолтные значения, поэтому необязательно их указывать.
Запустить скрипт вы можете командой:
```sh
python parse_auto.py
```
Рядом с файлом скрипта(`parse_auto.py`) создадутся две папки: `media` и `brands`.

В папке `media` будет хранится фотографии автомобилей и их логотипов, а в папке `brands` информация про автомобили каждого бренда.
## Как настроить скрипт парсера?
Настройка скрипта производится через переменные окружения.
Для этого нам понадобится в корне репозитория создать файл `.env`, в который записываются значения в формате `ПЕРЕМЕННАЯ=ЗНАЧЕНИЕ`.

Переменные, которые применяет скрипт:
- `BRAND_NAMES` — список с именами брендов, которые будет парсить скрипт. Имена указываются **через запятую и без пробела**.
- `BRANDS_FILENAME` — название json-файла, в котором хранятся сами бренды и ссылки  на их логотипы.
- `BRANDS_FOLDER` — папка, в которую сохранится файл, описанный выше, и json-файлы с объявлениями машин, распределенные по папкам.
- `CAR_IMG_FOLDER` — папка, которую сохраяются изображения машин с объявлений, разделенные по папкам брендов, а также логотипы этих брендов.
- `PAGE_COUNT` — количество спарсенных страниц бренда с автомобилями. Учитывайте что на одной странице `20` автомобилей.

    Также для удобства эту переменную можно указать аргументом в командной строке. 

    Пример:  `python parse_auto.py --page_count 5`.

    При указании переменной одновременно в `.env` и в командной строке, в приоритете 
    будет значение из `.env` файла.

Вот пример `.env`, заполненного дефолтными значенями:
```
BRAND_NAMES=bmw,lexus,ford,mazda,chevrolet,mercedes-benz
BRANDS_FILENAME=brands.json
BRANDS_FOLDER=brands
CAR_IMG_FOLDER=media
PAGE_COUNT=3
```
### Цели проекта
Код написан в учебных целях — это проект от основателей [Devman](https://dvmn.org).

