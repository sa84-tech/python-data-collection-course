from bs4 import BeautifulSoup as bs
import requests
import re
from pprint import pprint

JOBLIST_URL = 'https://spb.superjob.ru'
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0'}


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


def main():
    print('SuperJob Vacancy Analyzer')
    while True:
        position = input('Enter the name of the vacancy, q for exit: ')
        if position == 'q':
            print('Exit by user command.')
            break
        elif len(position) < 3:
            print('Minimum length - 3 characters')
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

            print('Result:')
            pprint(vacancies)
            print(f'Total number of vacancies for the position of an "{position}": {len(vacancies)}')

        else:
            print(f'Error: Something went wrong! Status code:', response.status_code)


if __name__ == '__main__':
    main()
