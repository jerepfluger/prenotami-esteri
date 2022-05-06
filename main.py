import argparse
import time

from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys


# FIXME: Instead of args I should use a JSON
parser = argparse.ArgumentParser()
parser.add_argument('--username', type=str, help='User account with which we\'ll login')
parser.add_argument('--password', type=str, help='Account password we\'ll use to login')
parser.add_argument('--appointment', type=str, choices=['PASAPORTE', 'CIUDADANIA DESCENDENCIA', 'CIUDADANIA PADRES'], help='Type of appointment you want to schedule')
parser.add_argument('--address', type=str, help='Your current address. The one in your ID')
parser.add_argument('--have_kids', type=str, choices=['SI', 'NO'], help='Do you have kids?')
parser.add_argument('--marital_status', type=str, choices=['CASADO', 'DIVORCIADO', 'VIUDO', 'SOLTERO', 'SEPARADO', 'UNION CIVIL', 'SEPARADO U/C', 'DIVORCIADO U/C', 'VIUDO U/C'], help='Do you have kids?')
parser.add_argument('--expired_passport', type=str, choices=['SI', 'NO'], help='Do you have an italian expired passport?')
parser.add_argument('--amount_minor_kids', type=str, help='Amount of minor kids you have?')


args = parser.parse_args()

USER = args.username
PASS = args.password
APPOINTMENT = args.appointment
ADDRESS = args.address
HAVE_KIDS = args.have_kids
MARITAL_STATUS = args.marital_status
EXPIRED_PASSPORT = args.expired_passport
AMOUNT_MINOR_KIDS = args.amount_minor_kids


def start_browser():
    options = FirefoxOptions()
    options.binary_location = '/Applications/Firefox.app/Contents/MacOS/firefox-bin'
    options.add_argument('--new_instance')
    #  https://developer.mozilla.org/en-US/docs/Mozilla/Preferences/Mozilla_networking_preferences
    options.set_preference('browser.cache.disk.enable', 'true')
    options.set_preference('browser.cache.memory.enable', 'true')
    # https://github.com/mozilla/geckodriver/issues/517#issuecomment-286701282
    options.set_preference("browser.tabs.remote.autostart", "false")
    options.set_preference("browser.tabs.remote.autostart.1", "false")
    options.set_preference("browser.tabs.remote.autostart.2", "false")
    options.set_preference("browser.tabs.remote.force-enable", "false")
    # more settings
    options.set_preference("dom.ipc.processCount", "1")
    options.set_preference("browser.sessionstore.interval", "50000000")
    options.set_preference("browser.sessionstore.max_resumed_crashes", "0")
    options.set_preference("browser.sessionstore.max_tabs_undo", "0")
    options.set_preference("browser.sessionstore.max_windows_undo", "0")
    options.set_preference("dom.popup_maximum", 0)
    options.set_preference("privacy.popups.showBrowserMessage", False)
    options.set_preference("privacy.popups.disable_from_plugins", 3)

    return webdriver.Firefox(options=options)


# TODO: Maybe we could add new appointment types
def select_appointment(driver, APPOINTMENT):
    if APPOINTMENT == 'PASAPORTE':
        return driver.get('https://prenotami.esteri.it/Services/Booking/104')
    if APPOINTMENT == 'CIUDADANIA DESCENDENCIA':
        return driver.get('https://prenotami.esteri.it/Services/Booking/340')
    if APPOINTMENT == 'CIUDADANIA PADRES':
        return driver.get('https://prenotami.esteri.it/Services/Booking/339')
    raise Exception('Unknown appointment type')


def return_full_marital_status(MARITAL_STATUS):
    if MARITAL_STATUS == 'CASADO':
        return 'Casado/a'
    if MARITAL_STATUS == 'DIVORCIADO':
        return 'Divorciado/a'
    if MARITAL_STATUS == 'VIUDO':
        return 'Viudo/a'
    if MARITAL_STATUS == 'SOLTERO':
        return 'Soltero/a'
    if MARITAL_STATUS == 'SEPARADO':
        return 'Separado/a'
    if MARITAL_STATUS == 'UNION CIVIL':
        return 'Unido/a civilmente'
    if MARITAL_STATUS == 'SEPARADO U/C':
        return 'Separado/a de Un. Civ.'
    if MARITAL_STATUS == 'DIVORCIADO U/C':
        return 'Divorciado/a de Un. Civ.'
    if MARITAL_STATUS == 'VIUDO U/C':
        return 'Viudo/a de Un. Civ.'
    raise Exception('Wrong Marital status')


def complete_passport_appointment_data(driver):
    address_input = driver.find_element(By.ID, 'DatiAddizionaliPrenotante_0___testo')
    address_input.send_keys(ADDRESS)

    have_kids_select = Select(driver.find_element(By.ID, 'ddls_1'))
    have_kids_select.select_by_visible_text(HAVE_KIDS.capitalize())

    marital_status = Select(driver.find_element(By.ID, 'ddls_2'))
    marital_status.select_by_visible_text(return_full_marital_status(MARITAL_STATUS))

    have_expired_passport = Select(driver.find_element(By.ID, 'ddls_3'))
    have_expired_passport.select_by_visible_text(EXPIRED_PASSPORT.capitalize())

    amount_minor_kids_input = driver.find_element(By.ID, 'DatiAddizionaliPrenotante_4___testo')
    amount_minor_kids_input.send_keys(AMOUNT_MINOR_KIDS)


def complete_family_citizenship(driver):
    marital_status = Select(driver.find_element(By.ID, 'ddls_0'))
    marital_status.select_by_visible_text(return_full_marital_status(MARITAL_STATUS))

    address_input = driver.find_element(By.ID, 'DatiAddizionaliPrenotante_1___testo')
    address_input.send_keys(ADDRESS)

    amount_minor_kids_input = driver.find_element(By.ID, 'DatiAddizionaliPrenotante_2___testo')
    amount_minor_kids_input.send_keys(AMOUNT_MINOR_KIDS)


def complete_appointment_details(driver, APPOINTMENT):
    if APPOINTMENT == 'PASAPORTE':
        # FIXME: This could also be an appointment for multiple people
        complete_passport_appointment_data(driver)
    if APPOINTMENT == 'CIUDADANIA PADRES':
        complete_family_citizenship(driver)
    # There's no need for completing any data for descendent citizenship appointment


class NeedsRetryException(Exception):
    def __init__(self, message):
        self.message = message


while True:
    try:
        driver = start_browser()
        driver.maximize_window()
        driver.get('https://prenotami.esteri.it/')
        # Waiting for login page to be fully loaded
        # FIXME: We need to select 'spanish' language
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'login-email')))
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # Complete username field
        username_input = driver.find_element(By.ID, 'login-email')
        username_input.send_keys(USER)
        # Complete password field
        password_input = driver.find_element(By.ID, 'login-password')
        password_input.send_keys(PASS)
        password_input.send_keys(Keys.ENTER)

        # Waiting for user area page to be fully loaded
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'advanced')))
        driver.get('https://prenotami.esteri.it/Language/ChangeLanguage?lang=13')
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'advanced')))
        prenotami_tab = driver.find_element(By.ID, 'advanced')
        driver.execute_script("arguments[0].click();", prenotami_tab)

        # Waiting for prenotami tab to be fully loaded
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'dataTableServices')))
        select_appointment(driver, APPOINTMENT)

        # Waiting for appointment page to be fully loaded
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'typeofbookingddl')))
        complete_appointment_details(driver, APPOINTMENT)

        privacy_check_box = driver.find_element(By.ID, 'PrivacyCheck')
        driver.execute_script("arguments[0].click();", privacy_check_box)

        avanti_button = driver.find_element(By.ID, 'btnAvanti')
        driver.execute_script("arguments[0].click();", avanti_button)

        driver.switch_to.alert.accept()

        try:
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, './/div[text()="Al momento non ci sono date disponibili per il servizio richiesto"]')))
            raise NeedsRetryException('No available appointments')
        except NoSuchElementException:
            pass

        loops = 1
        while True:
            if loops > 10:
                raise NeedsRetryException('No available appointments')
            available_dates = driver.find_elements(By.XPATH, './/td[@class="day availableDay"]')
            # TODO: Maybe we could take a screenshot in here. So we have 'proof' that in fact the selected appointment is the first one
            if len(available_dates) > 0:
                driver.execute_script("arguments[0].click();", available_dates[0])
                date_button = driver.find_elements(By.ID, 'idHiddenFasciaServizio')
                if len(date_button) > 0:
                    driver.execute_script("arguments[0].click();", date_button[0])

                    break

            next_month_button = driver.find_element(By.XPATH, './/span[@title="Next Month"]')
            driver.execute_script("arguments[0].click();", next_month_button)
            loops += 1

        # Accept appointment
        accept_appointment_button = driver.find_element(By.ID, 'btnPrenotaNoOtp')
        driver.execute_script("arguments[0].click();", accept_appointment_button)

        # Accept and close
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'btnStampa')))

        # TODO: We need to save this to send it to the client
        # driver.save_full_page_screenshot()
        break

    except Exception as ex:
        print(ex.__str__())
        try:
            driver.close()
            driver.quit()
        except NameError:
            pass
        if isinstance(ex, NeedsRetryException):
            time.sleep(60)
