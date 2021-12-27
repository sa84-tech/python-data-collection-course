import os
import re
import sys

from bs4 import BeautifulSoup as bs
import requests
from pprint import pprint
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))


JOBLIST_URL = 'https://spb.superjob.ru'
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0'}

DB_URI = os.environ.get('DB_URI')
DB_NAME = os.environ.get('DB_NAME')

try:
    CLIENT = MongoClient(DB_URI)
    DB = CLIENT[DB_NAME]
    print(DB)
except Exception as e:
    print(e)
    sys.exit(1)

vacancies_collection = DB.vacancies


def parse_salary_string(salary_string):
    salary = {}
    ss = re.sub(r'\s+', '', salary_string, flags=re.UNICODE)
    if re.search('договор', salary_string):
        salary['agreement'] = True
    else:
        try:
            values = [float(s) for s in re.findall(r'-?\d+\.?\d*', ss)]
        except ValueError:
            pass
        else:
            if re.search('от', salary_string):
                salary['min'] = values[0]
            elif re.search('до', salary_string):
                salary['max'] = values[0]
            elif re.search('—', salary_string):
                salary['min'] = values[0]
                salary['max'] = values[1]
            else:
                salary['exact'] = values[0]

    if re.search('руб.', salary_string):
        salary['currency'] = 'RUB'
    elif re.search('USD', salary_string):
        salary['currency'] = 'USD'
    elif re.search('EUR', salary_string):
        salary['currency'] = 'EUR'

    return salary


def parse_page(dom_obj, vacancies):
    joblist_data = dom_obj.find_all('div', {'class': 'f-test-vacancy-item'})

    for vacancy_item in joblist_data:
        vac_name_tag = vacancy_item.find('a')
        name = vac_name_tag.text
        link = vac_name_tag['href']
        salary_tag = vac_name_tag.parent.next_sibling
        salary = parse_salary_string(salary_tag.text)
        vacancies.append({'name': name, 'salary': salary, 'source': JOBLIST_URL, 'link': f'{JOBLIST_URL}{link}'})


def is_new(vacancies):
    new_vacancies = []
    for vacancy in vacancies:
        if not vacancies_collection.find_one({'link': vacancy['link']}):
            new_vacancies.append(vacancy)
    return new_vacancies


def update_db(collection, vacancies):
    new_vacancies = []
    print('Updating database...')
    try:
        for vacancy in vacancies:
            if not collection.find_one({'link': vacancy['link']}):
                new_vacancies.append(vacancy)
        created_vacancies = collection.insert_many(new_vacancies)
    except Exception as ee:
        print('Database Error: Something went wrong!')
        print(ee)
        return None
    else:
        print('Done.')
        return created_vacancies


def get_vacancies(collection):
    print(collection)
    # try:
    #     check_value = float(input('Enter minimum salary value: '))
    # except ValueError:
    #     print('Invalid salary value!')
    #     return None
    # obj = {'salary': {'$or': [
    #     {'salary': {'min': {'$gte': 100000}}},
    #     {'salary': {'max': {'$gte': 100000}}},
    #     {'salary': {'exact': {'$gte': 100000}}}
    # ]}}

    # obj = {'min': {'$gte': 100000}}
    # obj = {'agreement': True}

    obj = {'salary': {'agreement': True}}
    # obj = {'salary': {'currency': "RUB", 'min': {'$gte': 10000}}}
    # obj = {'salary': {'currency': "RUB", 'min': 100000}}

    # obj = {'salary': {'currency': "RUB", 'min': 100000}}
    print(obj)
    for doc in collection.find(obj):
        pprint(doc)
    # print(query_result)
    # result = collection.find({})
    # answer = [item for item in query_result]
    # pprint(answer)



def main():
    print('SuperJob Vacancy Analyzer')
    while True:
        menu_item = input('Type command: 1 - fetch new vacancies from source, '
                          '2 - display vacancies from db, q - quit the program')
        if menu_item == 'q':
            print('Exit by user command.')
            break
        elif menu_item == '2':
            result = get_vacancies(vacancies_collection)
            if result:
                print(result)
            else:
                print('No vacancies')

        elif menu_item == '1':
            position = input('Enter the name of the vacancy: ')
            if len(position) < 3:
                print('Minimum length - 3 characters')
                continue
            output = input('Type 1 for only new vacancies, 2 for all: ')
            if output not in ('1', '2'):
                print('Invalid input!')
                continue

            params = {'keywords': position}
            vacancies = []

            response = requests.get(f"{JOBLIST_URL}/vacancy/search/", params=params, headers=HEADERS)

            if response.ok:
                print('Parsing in progress...')
                dom = bs(response.text, 'html.parser')
                pages = dom.find('a', {'class': 'f-test-link-Dalshe'})
                parse_page(dom, vacancies)
                if pages:
                    try:
                        max_pages = int(pages.previous_sibling.text)
                    except ValueError:
                        print(f'Warning: Unable to fetch the total number of pages.\nFirst page output:')
                    else:
                        print(f'page 1 of {max_pages} completed.', end='\r')
                        for page in range(2, max_pages + 1):
                            params['page'] = page
                            response = requests.get(f"{JOBLIST_URL}/vacancy/search/", params=params, headers=HEADERS)
                            if response.ok:
                                dom = bs(response.text, 'html.parser')
                                parse_page(dom, vacancies)
                                print(f'page {page} of {max_pages} completed.  ', end='\r')
                            else:
                                print(f'Error: Unable to fetch data from page {page} of {max_pages}!\nPartial output:')
                                break
                print('Done! Processing result... ', end='\r')
                # new_vacancies = is_new(vacancies)
                new_vacancies = update_db(vacancies_collection, vacancies)
                if output == '1':
                    print(f'New Vacancies List (position "{position}"):')
                    pprint(new_vacancies)
                else:
                    print(f'Vacancies List (position "{position}"):')
                    pprint(vacancies)

                print(f'Total number of vacancies for the position of an "{position}": {len(vacancies)}')
                new_vacancies_count = len(new_vacancies.inserted_ids) if new_vacancies else 0
                print(f'Number of new vacancies: {new_vacancies_count}')
                #
                # print('Updating database...')
                # try:
                #     vacancies_collection.insert_many(new_vacancies)
                # except Exception as ee:
                #     print('Error: Something went wrong!')
                #     print(ee)
                # else:
                #     print('Done.')

            else:
                print(f'Error: Something went wrong! Status code:', response.status_code)


if __name__ == '__main__':
    main()
