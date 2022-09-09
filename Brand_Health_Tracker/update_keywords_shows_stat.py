import sqlite3
from sqlite3 import Error


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


def update_keywords_shows_stat(d_keyword, d_category, d_region, d_exact, d_wide, d_date):
    d_update_keywords = f"""
    INSERT INTO
      keywords_shows_stat (keyword, category, region, exact, wide, date)
    VALUES
      ('{d_keyword}', '{d_category}', '{d_region}', '{d_exact}', '{d_wide}', '{d_date}')
    """
    return d_update_keywords


connection = create_connection('/Users/mitya/keywords.sqlite')

with open('/Users/mitya/Downloads/keywords_stat.txt') as file:
    for line in file:
        keyword, category, region, exact, wide, date = line.strip().split(';')
        update_keywords = update_keywords_shows_stat(keyword, category, region, exact, wide, date)
        update_table = execute_query(connection, update_keywords)
        # print(keyword, category, region, exact, wide, date)
