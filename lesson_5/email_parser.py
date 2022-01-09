import os
import sys
from pprint import pprint
from time import sleep

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

from utils.db_init import MAIL_COLLECTION

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

wait = WebDriverWait(driver, 10)

elem = driver.find_element(By.XPATH, "//input[@name='password']")
elem.send_keys(EMAIL_PASSWORD)
elem.send_keys(Keys.ENTER)

actions = ActionChains(driver)
email_links = set()
last_item = None

while True:
    items = driver.find_elements(By.CSS_SELECTOR, 'a.js-letter-list-item')
    print('len(items):', len(items))
    if last_item == items[-1]:
        print('EXIT')
        break
    last_item = items[-1]
    for item in items:
        email_links.add(item.get_attribute('href'))
    actions.move_to_element(items[-1])
    actions.perform()
    print(len(email_links), items[-1].text)

print(len(email_links))
pprint(email_links)

sleep(10)

driver.close()
