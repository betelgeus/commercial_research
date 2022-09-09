import matplotlib.pyplot as plt
import sqlite3
from sqlite3 import Error
import time

print('Напиши название города: Москва, Санкт-Петербург, Краснодар, Казань, Ростов-на-Дону, Сочи')
region = input()
dates = []
y = ['Коммерческие', 'Грузовчикофф', 'Газелькин']


def create_connection(path):
    d_connection = None
    try:
        d_connection = sqlite3.connect(path)
        print("Connection to SQLite DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")

    return d_connection


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

select_date = "SELECT date FROM keywords_shows_stat"
date_list = execute_read_query(connection, select_date)
for date in date_list:
    date = str(date).replace("('", '').replace("',)", '')
    if date not in dates:
        dates += [date]
dates.sort(key=lambda x: time.mktime(time.strptime(x, "%m.%Y")))

keywords_shows = {x: [0 for i in range(len(dates))] for x in y}

select_keywords = f"SELECT * FROM keywords_shows_stat WHERE region = '{region}'"
keywords_shows_stat_dict = execute_read_query(connection, select_keywords)
for line in keywords_shows_stat_dict:
    id_keyword, keyword, category, region, exact, wide, date = str(line).strip().split(',')
    keyword, category, region, exact, wide, date = keyword.replace(" '", '').replace("'", ''), category.replace(" '", '').replace("'", ''), region.replace(" '", '').replace("'", ''), exact.replace(" ", ''), wide.replace(" ", ''), date.replace(" '", '').replace("')", '')
    if category == 'COM':
        keywords_shows['Коммерческие'][dates.index(date)] += int(exact)
    elif category == 'GAZ':
        keywords_shows['Газелькин'][dates.index(date)] += int(exact)
    elif category == 'GRUZ':
        keywords_shows['Грузовчикофф'][dates.index(date)] += int(exact)

for i in keywords_shows.items():
    if i[0] == 'Газелькин':
        gaz = sum(i[1]) / len(i[1])
    elif i[0] == 'Грузовчикофф':
        grz = sum(i[1]) / len(i[1])
    elif i[0] == 'Коммерческие':
        com = sum(i[1]) / len(i[1])
    cnt = len(i[1])

gaz_av, grz_av, com_av = 0, 0, 0

for i in keywords_shows.items():
    for j in i[1]:
        if i[0] == 'Газелькин':
            gaz_av += (gaz - j) ** 2
        elif i[0] == 'Грузовчикофф':
            grz_av += (grz - j) ** 2
        elif i[0] == 'Коммерческие':
            com_av += (com - j) ** 2

gaz_av, grz_av, com_av = (gaz_av / cnt) ** 0.5, (grz_av / cnt) ** 0.5, (com_av / cnt) ** 0.5

fig, ax = plt.subplots()
ax.stackplot(dates, keywords_shows.values(),
             labels=keywords_shows.keys(), alpha=0.8)
ax.hlines(com, dates[0], dates[-1], label='Среднее', colors='red', linestyle='--')
ax.hlines((com - com_av), dates[0], dates[-1], label='Среднее - Среднеквадратическое', colors='blue', linestyle='--')
ax.hlines((com + com_av), dates[0], dates[-1], label='Среднее + Среднеквадратическое', colors='blue', linestyle='--')
ax.text(0.0, 500000.0, f'Газелькин: {int(gaz_av)}, Грузовчикофф: {int(grz_av)}, Коммерческие: {int(com_av)}')
ax.grid(True, linestyle='-.')
ax.tick_params(labelcolor='r', labelsize='small', width=1)
ax.legend(loc='lower left')
plt.show()
