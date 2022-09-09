# программа парсит частотность ключевых запросов в Yandex Direct
# методы API Wordstat: https://yandex.ru/dev/direct/doc/dg-v4/reference/CreateNewWordstatReport.html
# ограничения: https://yandex.ru/dev/direct/doc/dg-v4/concepts/Restrictions.html
# коды ошибок и предупреждений: https://yandex.ru/dev/direct/doc/dg-v4/reference/ErrorCodes.html

import sqlite3
from sqlite3 import Error
import requests
import json
import time
from datetime import datetime
import math


direct_api_url = ['https://api.direct.yandex.ru/v4/json/', 'https://api-sandbox.direct.yandex.ru/v4/json/']
oauth_token = ''
keywords = []
create_report_id = []
keywords_dict = {}
done_reports = []
update_keywords = []
regions = ['Москва', 'Санкт-Петербург', 'Краснодар', 'Казань', 'Ростов-на-Дону', 'Сочи']
regions_id = [213, 2, 35, 239, 39, 43]
x, y = 0, 10
date = str(datetime.now().month - 1) + '.' + str(datetime.now().year)
cnt_reports_in_work = 0
cnt_done_keywords = 0
cycle = 0


def create_connection(path):
    d_connection = None
    try:
        d_connection = sqlite3.connect(path)
        print("Connection to SQLite DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")

    return d_connection


def execute_query(d_connection, query):
    cursor = d_connection.cursor()
    try:
        cursor.execute(query)
        d_connection.commit()
        print("Query executed successfully")
        return True
    except Error as e:
        print(f"The error '{e}' occurred")
        return False


def execute_read_query(d_connection, query):
    cursor = d_connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f"The error '{e}' occurred")


connection = create_connection('/Users/mitya/keywords.sqlite')


def create_new_report(d_keywords, d_region_id):
    cnt = 0
    d_report_id = 0
    data_new_report_request = {
        "method": "CreateNewWordstatReport",
        "param": {
            'Phrases': d_keywords,
            'GeoID': [d_region_id]
        },
        "locale": "ru",
        "token": oauth_token
    }
    data_new_report_request = json.dumps(data_new_report_request, ensure_ascii=False).encode('utf8')
    while d_report_id == 0:
        create_new_report_request = requests.post(direct_api_url[0], data_new_report_request)
        if cnt < 30:
            if create_new_report_request.status_code != 200 or \
                    create_new_report_request.json().get('error_code', False):
                print(f'Произошла ошибка при обращении к серверу API Директа. Код ответа сервера: '
                      f'{create_new_report_request.status_code}')
                print(f'Код ошибки: {create_new_report_request.json()["error_code"]}')
                print(f'Детали ошибки: {create_new_report_request.json()["error_detail"]}')
                print(f'Описание ошибки: {create_new_report_request.json()["error_str"]}')
                if create_new_report_request.json()["error_code"] == 56:
                    time.sleep(86400)
                cnt += 1
                if 0 <= cnt <= 5:
                    time.sleep(120)
                elif 5 < cnt <= 10:
                    time.sleep(360)
                elif 10 < cnt <= 15:
                    time.sleep(720)
                elif 15 < cnt <= 30:
                    time.sleep(1440)
            else:
                d_report_id = create_new_report_request.json()['data']
        else:
            break
    return d_report_id


def get_report_list():
    cnt = 0
    data_get_report_list = {
        "method": "GetWordstatReportList",
        "param": {},
        "locale": "ru",
        "token": oauth_token
    }
    data_get_report_list = json.dumps(data_get_report_list, ensure_ascii=False).encode('utf8')
    create_report_list_request = requests.post(direct_api_url[0], data_get_report_list)
    while 'Done' not in str(create_report_list_request.json()):
        create_report_list_request = requests.post(direct_api_url[0], data_get_report_list)
        if cnt < 30:
            if create_report_list_request.status_code != 200 or create_report_list_request.json().\
                    get('error_code', False):
                print(f'Произошла ошибка при обращении к серверу API Директа. Код ответа сервера: '
                      f'{create_report_list_request.status_code}')
                print(f'Код ошибки: {create_report_list_request.json()["error_code"]}')
                print(f'Детали ошибки: {create_report_list_request.json()["error_detail"]}')
                print(f'Описание ошибки: {create_report_list_request.json()["error_str"]}')
                if create_report_list_request.json()["error_code"] == 56:
                    time.sleep(86400)
                cnt += 1
                if 0 <= cnt <= 5:
                    time.sleep(120)
                elif 5 < cnt <= 10:
                    time.sleep(360)
                elif 10 < cnt <= 15:
                    time.sleep(720)
                elif 15 < cnt <= 30:
                    time.sleep(1440)
            else:
                continue
        else:
            break
    d_report_list = create_report_list_request.json()['data']
    return d_report_list


def update_keywords_shows_stat(d_keyword, d_category, d_region, d_exact, d_wide, d_date):
    d_update_keywords = f"""
    INSERT INTO
      keywords_shows_stat (keyword, category, region, exact, wide, date)
    VALUES
      ('{d_keyword}', '{d_category}', '{d_region}', '{d_exact}', '{d_wide}', '{d_date}')
    """
    return d_update_keywords


def get_wordstat_report(d_report_id):
    cnt = 0
    d_keywords_shows = 0
    data_report_request = {
        "method": "GetWordstatReport",
        "param": d_report_id,
        "locale": "ru",
        "token": oauth_token
    }
    data_report_request = json.dumps(data_report_request, ensure_ascii=False).encode('utf8')
    while d_keywords_shows == 0:
        get_shows_report_request = requests.post(direct_api_url[0], data_report_request)
        if cnt < 30:
            if get_shows_report_request.status_code != 200 or get_shows_report_request.json().get('error_code', False):
                print(f'Произошла ошибка при обращении к серверу API Директа. Код ответа сервера: '
                      f'{get_shows_report_request.status_code}')
                print(f'Код ошибки: {get_shows_report_request.json()["error_code"]}')
                print(f'Детали ошибки: {get_shows_report_request.json()["error_detail"]}')
                print(f'Описание ошибки: {get_shows_report_request.json()["error_str"]}')
                if get_shows_report_request.json()["error_code"] == 56:
                    time.sleep(86400)
                cnt += 1
                if 0 <= cnt <= 5:
                    time.sleep(120)
                elif 5 < cnt <= 10:
                    time.sleep(360)
                elif 10 < cnt <= 15:
                    time.sleep(720)
                elif 15 < cnt <= 30:
                    time.sleep(1440)
            else:
                d_keywords_shows = get_shows_report_request.json()['data']  # принимает значение вида [{'Phrase':
                # '"!газелькин"', 'GeoID': ['213'], 'SearchedAlso':...
        else:
            break
    return d_keywords_shows


def keywords_shows_stats(d_keywords_shows, d_keywords_dict, d_cnt_done_keywords):
    for d_keywords in d_keywords_shows:
        d_cnt_done_keywords += 1
        d_keyword = d_keywords['Phrase']
        d_category = d_keywords_dict[d_keywords['Phrase']]
        d_region = regions[regions_id.index(int(str(d_keywords['GeoID']).replace('[\'', '').replace('\']', '')))]
        d_exact = d_keywords['SearchedWith'][0]['Shows']
        if len(d_keywords['SearchedWith']) > 1:
            d_wide = d_keywords['SearchedWith'][1]['Shows']
        else:
            d_wide = 0
        d_update_keywords = update_keywords_shows_stat(d_keyword, d_category, d_region, d_exact, d_wide, date)
        update_result = execute_query(connection, d_update_keywords)
    return d_cnt_done_keywords


def delete_wordstat_report(def_report_id):
    del_wordstat_report_result = 0
    cnt = 0
    data_report_request = {
        "method": "DeleteWordstatReport",
        "param": def_report_id,
        "locale": "ru",
        "token": oauth_token
    }
    data_report_request = json.dumps(data_report_request, ensure_ascii=False).encode('utf8')
    while del_wordstat_report_result == 0:
        create_del_wordstat_report_request = requests.post(direct_api_url[0], data_report_request)
        if cnt < 30:
            if create_del_wordstat_report_request.status_code != 200 or create_del_wordstat_report_request.json().\
                    get('error_code', False):
                print(f'Произошла ошибка при обращении к серверу API Директа. Код ответа сервера: '
                      f'{create_del_wordstat_report_request.status_code}')
                print(f'Код ошибки: {create_del_wordstat_report_request.json()["error_code"]}')
                print(f'Детали ошибки: {create_del_wordstat_report_request.json()["error_detail"]}')
                print(f'Описание ошибки: {create_del_wordstat_report_request.json()["error_str"]}')
                if create_del_wordstat_report_request.json()["error_code"] == 56:
                    time.sleep(86400)
                cnt += 1
                if 0 <= cnt <= 5:
                    time.sleep(120)
                elif 5 < cnt <= 10:
                    time.sleep(360)
                elif 10 < cnt <= 15:
                    time.sleep(720)
                elif 15 < cnt <= 30:
                    time.sleep(1440)
            else:
                del_wordstat_report_result = create_del_wordstat_report_request.json()['data']
        else:
            break
    return del_wordstat_report_result


select_count_keywords = "SELECT count (*) FROM keywords"
cnt_keywords = execute_read_query(connection, select_count_keywords)
cnt_keywords = int(str(cnt_keywords).replace('[', '').replace('(', '').replace(',', '').replace(')', '')
                   .replace(']', ''))

for region_id in regions_id:
    while cnt_keywords - cnt_done_keywords > 0:  # выполняем цикл пока есть ключевики без статы по показам из Wordstat
        if (cnt_keywords - cnt_done_keywords) / 10 >= 5:
            cycle = 5
        elif (cnt_keywords - cnt_done_keywords) / 10 < 5:
            cycle = math.ceil((cnt_keywords - cnt_done_keywords) / 10)
        while cnt_reports_in_work < cycle:  # выполняем цикл пока отчетов в работе меньше 5 или достаточно для ключей
            select_keywords = f"SELECT keyword, category FROM keywords WHERE id > {x} AND id <= {y}"
            get_keywords = execute_read_query(connection, select_keywords)  # достаем запросы где id с X по Y
            for keyword in get_keywords:  # переменная keyword будет вида ('"!газелькин"', 'GAZ')
                keywords += [keyword[0]]  # добавляем "!газелькин" в список
                keywords_dict[keyword[0]] = keyword[1]  # добавляем '"!газелькин" и 'GAZ'в словарь
            report_id = create_new_report(keywords, region_id)  # создаем отчет в Wordstat по списку ключей
            create_report_id += [report_id]
            cnt_reports_in_work += 1
            x = y
            y += 10
            keywords = []
        while cnt_reports_in_work != 0:
            report_list = get_report_list()  # получаем список отчетов и их статусы
            for report_status in report_list:
                if report_status['StatusReport'] == 'Done' and report_status['ReportID'] in create_report_id:
                    done_reports += [report_status['ReportID']]  # добавляем в список готовых отчетов id отчета
            for report_id in done_reports:
                keywords_shows = get_wordstat_report(report_id)
                cnt_done_keywords = keywords_shows_stats(keywords_shows, keywords_dict, cnt_done_keywords)
                del_wordstat_report = delete_wordstat_report(report_id)
                if del_wordstat_report == 1:
                    cnt_reports_in_work -= 1
                    create_report_id.remove(report_id)
            done_reports = []
        create_report_id = []
    x, y = 0, 10
    cnt_done_keywords = 0
