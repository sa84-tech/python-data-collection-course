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

if not (DB_URI and DB_NAME):
    print('Add .env file with the variables DB_URI and DB_NAME.')
    sys.exit(1)

try:
    CLIENT = MongoClient(DB_URI)
    DB = CLIENT[DB_NAME]
except Exception as e:
    print('Error:', e)
    sys.exit(1)

VAC_COLLECTION = DB.vacancies


def parse_salary_string(salary_string):
    salary = {'min': 0, 'max': 0, 'currency': None}
    ss = re.sub(r'\s+', '', salary_string, flags=re.UNICODE)
    if re.search('договор', salary_string):
        return salary
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
                salary['min'] = values[0]

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


def insert_new_vacancies(collection, vacancies):
    new_vacancies = []
    for vacancy in vacancies:
        if not collection.find_one({'link': vacancy['link']}):
            try:
                collection.insert_one(vacancy)
                new_vacancies.append(vacancy)
            except Exception as ee:
                print('Database Error:', ee)
                return None
    return new_vacancies


def get_vacancies(collection, salary_value=0.0):
    print('Min salary:', salary_value)
    find_obj = {'$or': [
        {'salary.min': {'$gte': salary_value}},
        {'salary.max': {'$gte': salary_value}},
    ]}
    result = [item for item in collection.find(find_obj)]
    return result


def display_vacancies():
    try:
        salary_value = float(input('Enter the value of the minimum salary: '))
    except ValueError:
        print('Incorrect value!')
        return
    result = get_vacancies(VAC_COLLECTION, salary_value)
    if result:
        pprint(result)
        print(f'Total number of vacancies with salary above {salary_value}: {len(result)}')
    else:
        print('No vacancies')


def fetch_vacancies():
    position = input('Enter the name of the vacancy: ')
    if len(position) < 3:
        print('Minimum length - 3 characters')
        return

    only_new = input('Type 1 for only new vacancies, 2 for all: ')
    if only_new not in ('1', '2'):
        print('Invalid input!')
        return

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
                print(f'page 1 of {max_pages} completed.', end='')
                for page in range(2, max_pages + 1):
                    params['page'] = page
                    response = requests.get(f"{JOBLIST_URL}/vacancy/search/", params=params, headers=HEADERS)
                    if response.ok:
                        dom = bs(response.text, 'html.parser')
                        parse_page(dom, vacancies)
                        print(f'\rpage {page} of {max_pages} completed.  ', end='')
                    else:
                        print(f'Error: Unable to fetch data from page {page} of {max_pages}!\nPartial output:')
                        break
        print('\rDone! Processing result... ')

        new_vacancies = insert_new_vacancies(VAC_COLLECTION, vacancies)

        if only_new == '1':
            print(f'New Vacancies List (position "{position}"):')
            pprint(new_vacancies)
        else:
            print(f'Vacancies List (position "{position}"):')
            pprint(vacancies)

        print(f'Total number of vacancies for the position of an "{position}": {len(vacancies)}')
        print(f'Number of new vacancies: {len(new_vacancies)}')

    else:
        print(f'Error: Something went wrong! Status code:', response.status_code)


def main():
    print('SuperJob Vacancy Analyzer')
    while True:
        menu_item = input('Enter command: 1 - fetch new vacancies from SuperJob, '
                          '2 - display vacancies from db, q - quit the program: ')

        if menu_item == 'q':
            print('Exit by user command.')
            break

        elif menu_item == '1':
            fetch_vacancies()

        elif menu_item == '2':
            display_vacancies()


if __name__ == '__main__':
    main()
