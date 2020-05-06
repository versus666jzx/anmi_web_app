from datetime import datetime
import requests
from bs4 import BeautifulSoup
import json
from publication_destiny import publication_density

path = '/home/v/versus666/anmi.space/WebApp/'

proxies = {
    "http": "http://mishkapolar_gmail_co:46303f543b@37.221.83.137:30001",
    "https": "https://mishkapolar_gmail_co:46303f543b@37.221.83.137:30001",
}


def convert_id_to_shortcode(media_id: int) -> str:
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_'
    shortcode = ''
    while media_id > 0:
        remainder = media_id % 64
        media_id = (media_id - remainder) // 64
        shortcode = alphabet[remainder] + shortcode
    return shortcode


def get_statistics(username: str, min_time: str, max_time: str) -> dict:
    # переводим даты в timastamp
    max_timestamp = round(datetime.strptime(max_time + " 23:59:59", "%Y-%m-%d %H:%M:%S").timestamp())
    min_timestamp = round(datetime.strptime(min_time + " 00:00:00", "%Y-%m-%d %H:%M:%S").timestamp())
    # результат работы
    result_dict = {'user_id': '',
                   'avatar_url': '',
                   'is_fresh': 0,
                   'is_verified': 0,
                   'followed_by_count': 0,
                   'media_total': 0,
                   'media_in_period': 0,
                   'likes_in_period': 0,
                   'comments_in_period': 0,
                   'density': {},
                   'pages_loaded': 0,
                   'error_code': 0}
    # работаем в рамках одной сессии
    with requests.session() as session:
        # забираем параметры для сессии
        session_parameters = get_parameters("session")
        # добавляем proxy к сессии
        session.proxies = proxies
        # формируем заголовок для запроса
        session.headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 8.0.0; Pixel 2 XL Build/OPD1.170816.004) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Mobile Safari/537.36',
                           'Accept': '*/*',
                           'Accept-Encoding': 'gzip, deflate, br',
                           'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
                           'Connection': 'keep-alive',
                           'Content-Type': 'application/x-www-form-urlencoded',
                           'x-csrftoken': 'XH2Om6MEEaeAu0DBEyEl1Kmk5Gd2xfPp',  # None
                           'x-requested-with': 'XMLHttpRequest',
                           'x-instagram-ajax': 'ea494c0952c9',
                           'Host': 'www.instagram.com',
                           'Origin': 'https://www.instagram.com',
                           'Proxy-Authorization': 'Basic bWlzaGthcG9sYXJfZ21haWxfY286NDYzMDNmNTQzYg==',
                           'Referer': 'https://www.instagram.com',
                           'TE': 'Trailers'}
        login_data = get_parameters("login_data")
        session_login = session.post('https://www.instagram.com/accounts/login/ajax/', data=login_data, allow_redirects=True)
        print(session_login.text)
        if json.loads(session_login.text)["status"] == "ok":
            # получить user_id страницы, которую будем смотреть
            html_page_text = session.get(f"https://www.instagram.com/{username}/").text
            html_by_soup = BeautifulSoup(html_page_text, 'lxml')
            data_from_html = None
            user_id = ""
            for tag in html_by_soup.find_all("script"):
                if str(tag.text).startswith("window._sharedData"):
                    whole_json = json.loads(str(tag.text)[str(tag.text).find("{"):-1])
                    data_from_html = whole_json["entry_data"]["ProfilePage"][0]["graphql"]["user"]
                    user_id = data_from_html["id"]
                    # print(whole_json["config"]["csrf_token"])
                    if session.headers["x-csrftoken"] != whole_json["config"]["csrf_token"]:
                        session.headers.update({'x-csrftoken': whole_json["config"]["csrf_token"]})
                        session.headers.update({'x-instagram-ajax': whole_json["rollout_hash"]})
                        set_parameters("session", {'csrf_token': whole_json["config"]["csrf_token"],
                                                   'rollout_hash': whole_json["rollout_hash"]})
                    break
            # если получилось добыть какие-то данные
            # проверяем страницу на приватность
            if data_from_html["is_private"]:
                result_dict["error_code"] += 100
            else:
                if data_from_html:
                    # сначала заполняем поля пользователя
                    result_dict.update({'user_id': data_from_html["id"],
                                        'avatar_url': '' if str(data_from_html["profile_pic_url"]).count("5E695BF1") else str(data_from_html["profile_pic_url"]).replace("&amp;", "&"),
                                        'is_fresh': 1 if data_from_html["is_joined_recently"] else 0,
                                        'is_verified': 1 if data_from_html["is_verified"] else 0,
                                        'followed_by_count': data_from_html["edge_followed_by"]["count"],
                                        'media_total': data_from_html["edge_owner_to_timeline_media"]["count"]})
                # end_cursor нужен для подгрузки следующих страниц с постами
                end_cursor = ""
                # счётчик загруженных страниц
                page_counter = 0
                # список тиймштампов для вычислдения плотности
                timestamps_list = []
                # в цикле будем перебирать посты и подгружать новые, если понадобится
                # условием выхода из цикла будет несоответствие очередного поста диапазону поиска
                while True:
                    # получаем страницу в html
                    # в запрос подсовываем end_cursor, чтобы подгружать следующие страницы
                    user_data_as_json = json.loads(session.get("https://instagram.com/graphql/query/", params={'query_id': 17888483320059182,
                                                                                                               'id': user_id,
                                                                                                               'first': 12,
                                                                                                               'after': end_cursor}).text)["data"]["user"]
                    # увеличиваем счётчик страниц
                    page_counter += 1
                    # если получилось добыть какие-то данные
                    if user_data_as_json:
                        # сначала заполняем поля пользователя
                        result_dict.update({'pages_loaded': page_counter})
                        # теперь заполняем поля медиа
                        # print(len(user_data_as_json["edge_owner_to_timeline_media"]["edges"]))
                        # print([media["node"]["shortcode"] for media in user_data_as_json["edge_owner_to_timeline_media"]["edges"]])
                        for media in user_data_as_json["edge_owner_to_timeline_media"]["edges"]:
                            # если рассматриваемое медиа опубликовано раньше заданного периода времени
                            if media["node"]["taken_at_timestamp"] < min_timestamp:
                                # конец - дальше искать не нужно
                                result_dict['density'] = publication_density(timestamps_list)
                                return result_dict
                            # если рассматриваемое медиа опубликовано в заданный период времени
                            elif max_timestamp >= media["node"]["taken_at_timestamp"] >= min_timestamp:
                                # учитываем все атрибуты этого медиа в статистике
                                result_dict.update({'media_in_period': result_dict["media_in_period"] + 1,
                                                    'likes_in_period': result_dict["likes_in_period"] + media["node"]["edge_media_preview_like"]["count"],
                                                    'comments_in_period': result_dict["comments_in_period"] + media["node"]["edge_media_to_comment"]["count"]})
                                timestamps_list.append(media["node"]["taken_at_timestamp"])
                        # запоминаем новый end_cursor
                        if user_data_as_json["edge_owner_to_timeline_media"]["page_info"]["has_next_page"]:
                            end_cursor = user_data_as_json["edge_owner_to_timeline_media"]["page_info"]["end_cursor"]
                        else:
                            break
        else:
            result_dict["error_code"] += 1000
        return result_dict


def get_word_form(word: str, number: int) -> str:
    if str(number)[-2:] in ("11", "12", "13", "14"):
        if word[-1] == "й":
            return word[:-1] + "ев"
        else:
            return word + "ов"
    else:
        if word[-1] == "й":
            return word[:-1] + ("й" if str(number)[-1] == "1" else "я" if str(number)[-1] in ("2", "3", "4") else "ев")
        else:
            return word + ("" if str(number)[-1] == "1" else "а" if str(number)[-1] in ("2", "3", "4") else "ов")


def get_number_order(number: int) -> str:
    if len('{0:,}'.format(number).split(',')) == 1:
        return '{0:,}'.format(number).split(',')[0]
    else:
        if '{0:,}'.format(number).split(',')[1][0] == "0":
            return '{0:,}'.format(number).split(',')[0]
        else:
            return '{0:,}'.format(number).split(',')[0] + "." + '{0:,}'.format(number).split(',')[1][0]


def get_order_letter(number: int) -> str:
    return "М" if len('{0:,}'.format(number).split(',')) == 3 else "Т" if len('{0:,}'.format(number).split(',')) == 2 else ""


def get_parameters(parameter_section_name: str) -> dict:
    """
    There is a file settings.json in which all the parameters are sectioned by places of application.
    This method allows to get all the parameters from any section in one dictionary.

    :param parameter_section_name: name of some section to get parameters from
    :return: dictionary of parameters
    """
    with open(path + 'settings.json', 'r') as json_file:
        parameters_as_json = json.load(json_file)
        if parameter_section_name in parameters_as_json:
            return parameters_as_json[parameter_section_name]
        else:
            return None


def set_parameters(parameter_section_name: str, params: dict) -> dict:
    """
    There is a file settings.json in which all the parameters are sectioned by places of application.
    This method allows to set values for this parameters.

    :param parameter_section_name: name of some section
    :param params: dictionary of parameters names with values
    :return: 0 if parameters were set successfully and 1 otherwise
    """
    with open(path + 'settings.json', 'r') as json_file:
        parameters_as_json = json.load(json_file)
        if parameter_section_name in parameters_as_json:
            parameters_as_json[parameter_section_name] = params
        else:
            return 1
    with open(path + 'settings.json', 'w') as json_file:
        json.dump(parameters_as_json, json_file, indent=4)
        return 0