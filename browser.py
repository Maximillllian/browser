from sys import exit
from os import mkdir
from json import dump, dumps, loads
from pathlib import Path
from bs4 import BeautifulSoup
from colorama import Fore, Style
import argparse
import requests


class Browser:

    # Определены названия файлов, в которое будет сохраняться кэш. У меня реализован кэш двух видов: для доступа к
    # сайту по краткой ссылке и для опции назад (вводишь back и показывается прошлая страница). cash_name - кэш по
    # краткой ссылке, cash_back_name - для опции back
    # Мы будем использовать json файлы
    cash_name = 'cash.json'
    cash_back_name = 'tb_tabs.json'

    def __init__(self):

        # Так как браузер работает из коммандной строки, то сначала нужно спарсить аргумент из нее (директория, куда
        # сохраняется кэш
        self.parse_arg()

        # И создать кэш файлы
        self.create_cash_files()

    def open_cash_file(func):
        """Функция обертка, отвечает за открытие файла с кэшем"""
        def wrapper(self, *args, **kwargs):

            # С помощью класса Path из библиотеки pathlib создаем объект-путь нашего кэш-файла
            file_path = Path(f'{self.path}/{self.cash_name}')

            # Применим функцию read_text (то есть откроем файл) и скормим этот файл декодировщику json loads
            json_data = loads(file_path.read_text(encoding='utf-8'))

            # Передаем данные из файла функции, которая с ним будет колдовать
            res = func(self, json_data=json_data, *args, **kwargs)

            # Запишем данные обратно в файл, предварительно закодировав функцией dumps для json
            file_path.write_text(dumps(res), encoding='utf-8')
            return res
        return wrapper

    def open_cashback_file(func):
        """Функция обертка, отвечает за открытие файла с кэшем для загрузки прошлой страницы(опция back)"""
        def wrapper(self, *args, **kwargs):

            # Все то же самое, что и в прошлой функции-обретке, только изменилось название файла
            file_path = Path(f'{self.path}/{self.cash_back_name}')
            json_data = loads(file_path.read_text(encoding='utf-8'))
            res = func(self, json_data=json_data, *args, **kwargs)
            file_path.write_text(dumps(res), encoding='utf-8')
            return res
        return wrapper

    def parse_arg(self):
        """Парсим аргумент коммандной строки. Получаем название директории, куда сохраняем кэш"""

        # Создаем парсер
        parser = argparse.ArgumentParser()

        # Добавляем ему аргумент dir (директория, куда сохраняем кэш)
        parser.add_argument('dir')

        # Парсим и записываем в переменную self.path название папки
        file_dir = parser.parse_args()
        self.path = file_dir.dir

    def create_cash_files(self):
        """Создаем директорию и кэш файлы!"""

        # Пробуем создать директорию, если вылезает ошибка, значит она создана
        try:
            mkdir(self.path)
        except:
            pass

        # Создаем пустые файлы. В обычном кэше будет объект типа словаря, в кэшэ для прошлой страницы - список
        with open(f'{self.path}/{self.cash_name}', 'w+') as file:
            dump({}, file)
        with open(f'{self.path}/{self.cash_back_name}', 'w+') as file:
            dump([], file)

    # Оборачиваем функцю. Таким образом передаем ей данные из json файла
    @open_cash_file
    def create_cash(self, json_data, user_url, content):
        """
        Добавляем кэш в файл. Он будет такого вида {site_name_1: content_1, site_name_2: content_2}
        Название сайта превратим из https://google.com в google
        """

        # Сначала обрежем .com (или другие расширегия сайта)

        # Для этого найдем индекс последней точки в названии сайта
        index = user_url.rindex('.')

        # Обрежем название сайта до точки
        abbreviated_site = user_url[:index]

        # Если сайт содержит https:// - обрежем и его
        if abbreviated_site.startswith('https://'):
            abbreviated_site = abbreviated_site[8:]

        # Если сайт содержит www. - обрезаем это
        if abbreviated_site.startswith('www.'):
            abbreviated_site = abbreviated_site[4:]

        # Запишем название сайта и контент, который мы получили в словарь
        json_data[abbreviated_site] = content

        # Передадим словарь обертке, которая его запишет в файл
        return json_data

    def get_cash(self, user_url):
        """
        Ищем сайт в кэше. Если есть - вощвращаем его. Функцию обертку не используем, потому что она требует при ее
        использовании мы должны вернуть данные для записи в json-файл, а наша фунцкия возвращает контент сайта
        """

        # Загружаем данные из файла кэша (то же самое, что делаем в функции обертке)
        json_data = loads(Path(f'{self.path}/{self.cash_name}').read_text(encoding='utf-8'))

        # Если в данных содержится сайт, то возвращаем его контент
        try:
            if user_url in json_data:
                return json_data[user_url]

        # В противном случае не делаем ничего
        except:
            pass

    @open_cashback_file
    def create_cash_back(self, json_data, content):
        """Добавляем данные страницы в кэш для опции back"""

        # Когда загружаем страницу, просто добавляем ее контент в файл кэша для возврата на прошлую страницу
        json_data.append(content)
        return json_data

    @open_cashback_file
    def back(self, json_data):
        """Опция 'Вернуться на прошлую страницу' """
        try:

            # Вытаскиваем предпоследний элемент из данных (потому что последний - это страница, которая загружена сейча
            back = json_data.pop(-2)

            # И печатаем ее
            print(back)
            return json_data
        except:
            pass

    def make_request(self, user_url):
        """Сделаем запрос на сайт, если не сможем по каким либо причинам, не будем возвращать ничего"""
        try:

            # Модифицируем url. Если он не начнается с https://, то добавим этот протокол
            if not user_url.startswith('https://'):
                full_url = 'https://' + user_url
            else:
                full_url = user_url

            # Сделаем запрос и вернем объект запроса
            r = requests.get(full_url)
            return r
        except:
            return None

    def show_site(self, r):
        """Функция показывает сайт"""
        if r:

            # Вытаскиваем текст страницы из запроса
            content = r.text

            # С помощью класса BeautifulSoup из библиотеки beautifulsoup4 будем парсить HTML код
            soup = BeautifulSoup(content, 'html.parser')

            # Вытаскиваем все строчки, которые содержат тэги, в которых текст, отображенный на странице
            final_text = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'a', 'ul', 'ol'])
            # Преобразуем полученные строчки в str и добавим в список
            lst_final_text = []
            for i in final_text:

                # Мы покрасим весь текст, который является ссылкой в синий. Используем библиотеку colorama
                if i.name == 'a':

                    # С помощью метода text мы убираем тэги, в результате остается только текст, который между ними
                    lst_final_text.append(Fore.BLUE + str(i.text) + Style.RESET_ALL)
                else:
                    lst_final_text.append(str(i.text))

            # Создаем кэши
            self.create_cash(user_url=r.url, content=lst_final_text)
            self.create_cash_back(content=lst_final_text)

            # Печаетаем текст
            print(*lst_final_text, sep='\n')

    def get_url(self):
        """основная фунцкия. Спрашивает у пользователя URL и печает ответ"""
        while True:

            # Спросим URL у пользователя
            user_url = input()

            # Если фунцкия get_cash выдает что-то, значит сайт есть в кэше
            if self.get_cash(user_url=user_url):
                cash = self.get_cash(user_url=user_url)

                # Создаем кэш для опции back
                self.create_cash_back(content=cash)

                # Печатаем кэш
                print(cash)

            # Если мы смогли сделать запрос, то печатакем контент оттуда
            elif self.make_request(user_url):
                r = self.make_request(user_url)
                self.show_site(r)

            # Если пользователь ввел exit, значит он хочет выйти
            elif user_url == 'exit':
                exit()

            # Если back - посмотреть прошлую страницу
            elif user_url == 'back':
                self.back()

            # Если ни одно из условий не выполнено, значит введен некорректный url
            else:
                print('Error: Incorrect URL')


if __name__ == '__main__':
    chrome = Browser()
    chrome.get_url()
