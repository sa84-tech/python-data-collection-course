import os
import sys

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import WebDriverException

from utils.db_init import MAIL_COLLECTION
from utils.helpers import parse_date, get_id

EMAIL_ADDRESS = os.environ.get('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')

service = Service(executable_path='./utils/chromedriver.exe')
chrome_options = Options()
chrome_options.add_argument('start-maximized')

try:
    driver = webdriver.Chrome(service=service, options=chrome_options)
except WebDriverException:
    print('Add the executable file "chromedriver.exe" to the utils directory')
    sys.exit(1)

driver.implicitly_wait(5)

driver.get('https://mail.ru')

elem = driver.find_element(By.XPATH, "//input[@name='login']")
elem.send_keys(EMAIL_ADDRESS)
elem.send_keys(Keys.ENTER)

elem = driver.find_element(By.XPATH, "//input[@name='password']")
elem.send_keys(EMAIL_PASSWORD)
elem.send_keys(Keys.ENTER)

email_links = set()
last_item = None

print("Email Picker")

while True:
    items = driver.find_elements(By.CSS_SELECTOR, 'a.js-letter-list-item')
    if last_item == items[-1]:
        break
    last_item = items[-1]
    for item in items:
        email_links.add(item.get_attribute('href'))

    ActionChains(driver)\
        .move_to_element(items[-1])\
        .perform()

    print(f'\rEmails count: {len(email_links)}', end='...')

print(f'\rEmails count: {len(email_links)}    ')

for i, email_link in enumerate(email_links, 1):
    print(f'\rProcessing {i} email from {len(email_links)}', end='')

    email = {'_id': get_id(email_link)}

    if MAIL_COLLECTION.find_one(email):
        continue

    driver.get(email_link)
    email['author'] = driver.find_element(By.CSS_SELECTOR, 'span.letter-contact').get_attribute('title')
    email['date'] = parse_date(driver.find_element(By.CSS_SELECTOR, 'div.letter__date').text)
    email['subject'] = driver.find_element(By.CSS_SELECTOR, 'h2.thread-subject').text
    email['body'] = driver.find_element(By.CSS_SELECTOR, "div.letter__body").text

    MAIL_COLLECTION.insert_one(email)

print('\nDone.')

driver.close()
