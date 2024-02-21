### Python 3.8
import sqlite3
import time
import random
from datetime import date
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException, \
    ElementClickInterceptedException, TimeoutException
from selenium.common import exceptions


# Suche nach scroller class -> monatsliste
# durchgehen der Elemente der Monatsliste

# container aufrufen
# tageselemente aufrufen mit bindonce class = 'column' und 'column sat' und 'column sun'
# elemente durchgehen mit bindonce class='cell'
# speichern von date-id, jetztige zeit, calendar-price

# brandenburg, koln-bonn, prague, london-stansted, manchester, neapel, stockholm-skavsta, warsaw-modlin
flight_list = [['malaga', 'karlsruhe'],
               ['karlsruhe', 'malaga'],
               ['bremen', 'malaga'],
               ['malaga', 'bremen'],
               ['bristol', 'malaga'],
               ['malaga', 'bristol'],
               ['edinburgh', 'malaga'],
               ['malaga', 'edinburgh'],
               ['dublin', 'malaga'],
               ['malaga', 'dublin'],
               ['karlsruhe', 'malta'],
               ['malta', 'karlsruhe'],
               ['köln', 'manchester'],
               ['manchester', 'köln'],
               ['memmingen', 'malaga'],
               ['malaga', 'memmingen'],
               ['manchester', 'malaga'],
               ['edinburgh', 'malaga'],
               ['neapel', 'malaga']]
               #['warschau', 'malaga']

flight_date_price_list = []

# creates url for specific flight out of flight_list and returns a list of urls, departure airport, arrival airport, current date
def create_url(flight_list):
    random.shuffle(flight_list)
    flight_data_list = []
    current_date = date.today()
    start_date = current_date.isoformat()
    end_date = current_date.replace(year=current_date.year + 1).isoformat()
    print('This will be scrapped now:')
    for flight in flight_list:
        departure = flight[0]
        arrival = flight[1]
        url = 'https://www.ryanair.com/de/de/billige-fluege/' + departure + '-nach-' + arrival + '?out-from-date=' + start_date + '&out-to-date=' + end_date + '&budget=300'
        # e.g. https://www.ryanair.com/de/de/billige-fluege/malaga-nach-karlsruhe-baden?out-from-date=2021-01-02&out-to-date=2022-01-02&budget=200
        flight_data = [url, departure, arrival, current_date]
        flight_data_list.append(flight_data)
        print(flight[0]+' to '+flight[1])
    return flight_data_list

def login_to_flight(browser, flight):
    xpath_departure_box = '//*[@id="route-map-widget"]/searchbox-widget/div/div/div[1]/div[1]/input'
    xpath_autocomplete_d = '//*[@id="route-map-widget"]/searchbox-widget/map-widget-autocomplete/div/div/div[2]/div/ul/li'
    xpath_arrival_box = '//*[@id="route-map-widget"]/searchbox-widget/div/div/div[1]/div[2]/input'
    xpath_autocomplete_a = '//*[@id="route-map-widget"]/searchbox-widget/map-widget-autocomplete/div/div/div[2]/div/ul/li'
    xpath_book_flights = '/html/body/div[2]/main/div/farefinder-card/div/div/farefinder-card-details/div[2]/div[3]/div[1]/button'

    browser.get('https://www.ryanair.com/de/de/preiswerte-flugziele')
    time.sleep(random.randint(5, 7))
    flag = 3
    while flag > 0:
        try:
            WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, xpath_departure_box))).clear()
        except TimeoutException:
            login_to_flight(browser, flight)
            flag = flag - 1
        time.sleep(1)
        try:
            browser.find_element_by_xpath(xpath_departure_box).send_keys((flight[1])[0:random.randint(3, len(flight[1]))])
        except ElementNotInteractableException:
            flag -= 1
            continue
        time.sleep(1)
        try:
            browser.find_element_by_xpath(xpath_autocomplete_d).click()
        except ElementNotInteractableException:
            flag -= 1
            continue
        time.sleep(1)
        browser.find_element_by_xpath(xpath_arrival_box).clear()
        time.sleep(1)
        try:
            browser.find_element_by_xpath(xpath_arrival_box).send_keys((flight[2])[0:random.randint(3, len(flight[1]))])
        except ElementNotInteractableException:
            flag -= 1
            continue
        time.sleep(1)
        try:
            browser.find_element_by_xpath(xpath_autocomplete_a).click()
        except ElementNotInteractableException:
            flag -= 1
            continue
        time.sleep(1)
        try:
            browser.find_element_by_xpath(xpath_book_flights).click()
        except ElementNotInteractableException:
            flag -= 1
            continue
        time.sleep(1)
        flag = 0


def first_call(browser):
    browser.get('https://www.ryanair.com/de/de')
    try:
        browser.find_element_by_class_name('cookie-popup-with-overlay__button').click()
    except NoSuchElementException:
        pass



def call_urls(flight_data_list):
    counter = len(flight_data_list)+1
    for flight in flight_data_list:
        counter -= 1
        #options = webdriver.ChromeOptions()
        #options.add_argument("headless")
        browser = webdriver.Chrome('./chromedriver.exe')
        #options = browser.ChromeOptions()
        #options.add_experimental_option('excludeSwitches', ['enable-logging'])
        startcounter = 3
        while startcounter > 0:
            first_call(browser)
            time.sleep(2)
            try:
                login_to_flight(browser, flight)
            except:
                startcounter -= 1
                continue
            time.sleep(3)
            try:             # changes view to monthly view
                WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/main/div/div/div[1]/div[1]/div[2]/button[2]/span'))).click()
            except TimeoutException:
                print('\'Nach Monat sortiert anzeigen\'n  wurde nach 10s nicht gefunden')
                startcounter -= 1
                continue
            startcounter = 0
        time.sleep(2)
        print('Let us scrape the flight from '+flight[1]+' to '+flight[2])
        scrape_n_cyle_months(browser, flight)
        browser.quit()
        print('Finished with the flight from '+flight[1]+' to '+flight[2])
        print(str(counter - 1) + ' flights left...')
        print('Waiting some Seconds...')
        time.sleep(random.randint(1, 30))



# switches through the month tables
def scrape_n_cyle_months(browser, flight):
    month_counter = 15
    time.sleep(random.randint(1, 4))
    """back_counter = 7
    while(back_counter>0):
        try:
            WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/main/div/div/div[1]/div[2]/div/div/div[1]/button'))).click()
        except TimeoutException:
            break
        back_counter -= 1"""
    while(month_counter>0):
        try:
            browser.find_element_by_xpath('/html/body/div[2]/main/div/div/div[1]/div[2]/div/div/div[2]/div/ul/li['+str(month_counter)+']').click()
            time.sleep(0.2)
        except (ElementNotInteractableException, ElementClickInterceptedException, NoSuchElementException):
            pass
        month_counter = month_counter -1
    time.sleep(1)
    while month_counter < 15:
        #         /html/body/div[2]/main/div/div/div[1]/div[2]/div/div/div[2]/div/ul/li[5]
        x_path = '/html/body/div[2]/main/div/div/div[1]/div[2]/div/div/div[2]/div/ul/li['+str(month_counter)+']'
        month_counter += 1
        try:
            browser.find_element_by_xpath(x_path).click()
        except (ElementNotInteractableException, ElementClickInterceptedException, NoSuchElementException):
            continue
        time.sleep(random.randint(1, 3))
        scrape_flights(browser, flight)





def scrape_flights(browser, flight):
    week_counter = 2
    while week_counter <= 7:
        day_counter = 1
        while day_counter <= 7:
            x_path_short = '/html/body/div[2]/main/div/div/div[1]/div[4]/core-calendar/div/ul/li['+str(day_counter)+']/ul/li['+str(week_counter)+']'
            x_path_deep = '/html/body/div[2]/main/div/div/div[1]/div[4]/core-calendar/div/ul/li['+str(day_counter)+']/ul/li['+str(week_counter)+']/div[2]/calendar-monthly-template/div/p'
            day_counter += 1
            try:
                flight_price_raw = browser.find_element_by_xpath(x_path_deep).text
                if len(flight_price_raw) > 0:
                    #print(flight_price_raw + " Datatype: " + str(type(flight_price_raw)))
                    flight_price = float(flight_price_raw.replace('.', '').replace(',', '.').replace('€', '').replace('£', '').strip())/100
                    flight_date = datetime.strptime(browser.find_element_by_xpath(x_path_short).get_attribute('date-id').strip(), '%d-%m-%Y').date()
                    list_element = [flight_price, flight_date, flight[1], flight[2], flight[3]]
                    flight_date_price_list.append(list_element)
                    print(list_element)
            except NoSuchElementException:
                continue
            except exceptions.StaleElementReferenceException:
                print('StaleElementReferenceException')
                continue

        week_counter += 1
    print('Another month from '+flight[1]+' to '+flight[2]+' was scrapped successfull')

def write_to_database(flight_date_price_list, conn, c):
    for item in flight_date_price_list:
        c.execute('''INSERT INTO flights VALUES(?, ?, ?, ?, ?)''',
                  (item[0], item[1], item[2], item[3], item[4]))
        #price FLOAT, flight_date Date, departure_airport TEXT, arrival_airport TEXT, scrape_date Date)''')
    conn.commit()
    print('Everything written in database')

def main():
    print('Scraper starts... ')
    conn = sqlite3.connect('ryanair_db.db')
    c = conn.cursor()
    print('DB-Connection established..')
    flight_data_list = create_url(flight_list)
    call_urls(flight_data_list)
    write_to_database(flight_date_price_list, conn, c)
    conn.close()
    print('Adios...')
    while True:
        pass

# ____________ Here it starts  __________________          #####

main()
