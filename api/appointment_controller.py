import json
import time

from flask import request
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from config.config import settings as config_file
from webdrivers.webdriver import WebDriver
from . import routes


@routes.route("/prenotami-esteri/schedule_appointment", methods=["POST"])
def basic_instagram_crawler():
    appointment_data = json.loads(request.data)
    # FIXME: Sanitize data here
    try:
        driver = WebDriver().acquire(config_file.crawling.appointment_controller.webdriver_type)
        driver.maximize_window()
        driver.get('https://prenotami.esteri.it/')
        # Waiting for login page to be fully loaded
        # FIXME: We need to select 'spanish' language
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'login-email')))
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # Complete username field
        username_input = driver.find_element(By.ID, 'login-email')
        username_input.send_keys(appointment_data['user'])
        # Complete password field
        password_input = driver.find_element(By.ID, 'login-password')
        password_input.send_keys(appointment_data['pass'])
        password_input.send_keys(Keys.ENTER)

        # Waiting for user area page to be fully loaded
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'advanced')))
        driver.get('https://prenotami.esteri.it/Language/ChangeLanguage?lang=13')
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'advanced')))
        prenotami_tab = driver.find_element(By.ID, 'advanced')
        driver.execute_script("arguments[0].click();", prenotami_tab)

        # Waiting for prenotami tab to be fully loaded
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'dataTableServices')))
        select_appointment(driver, appointment_data['appointment_type'])

        # Waiting for appointment page to be fully loaded
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'typeofbookingddl')))
        complete_appointment_details(driver, appointment_data)

        privacy_check_box = driver.find_element(By.ID, 'PrivacyCheck')
        driver.execute_script("arguments[0].click();", privacy_check_box)

        avanti_button = driver.find_element(By.ID, 'btnAvanti')
        driver.execute_script("arguments[0].click();", avanti_button)

        driver.switch_to.alert.accept()

        try:
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, './/section[@class="calendario"]')))
        except NoSuchElementException:
            raise NeedsRetryException('No available appointments')

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

    except Exception as ex:
        print(ex.__str__())
        try:
            driver.close()
            driver.quit()
        except NameError:
            pass
        if isinstance(ex, NeedsRetryException):
            time.sleep(60)


# TODO: Maybe we could add new appointment types
def select_appointment(driver, APPOINTMENT):
    if APPOINTMENT == 'PASAPORTE':
        return driver.get('https://prenotami.esteri.it/Services/Booking/104')
    if APPOINTMENT == 'CIUDADANIA DESCENDENCIA':
        return driver.get('https://prenotami.esteri.it/Services/Booking/340')
    if APPOINTMENT == 'CIUDADANIA PADRES':
        return driver.get('https://prenotami.esteri.it/Services/Booking/339')
    if APPOINTMENT == 'VISADOS':
        return driver.get('https://prenotami.esteri.it/Services/Booking/753')
    if APPOINTMENT == 'DOCUMENTOS DE IDENTIDAD Y DE VIAJE':
        return driver.get('https://prenotami.esteri.it/Services/Booking/645')
    raise Exception('Unknown appointment type')


def return_full_marital_status(MARITAL_STATUS):
    MARITAL_STATUS = MARITAL_STATUS.upper()
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


def complete_passport_appointment_data(driver, appointment_data):
    address_input = driver.find_element(By.ID, 'DatiAddizionaliPrenotante_0___testo')
    address_input.send_keys(appointment_data['address'])

    have_kids_select = Select(driver.find_element(By.ID, 'ddls_1'))
    have_kids_select.select_by_visible_text(appointment_data['have_kids'].capitalize())

    marital_status = Select(driver.find_element(By.ID, 'ddls_2'))
    marital_status.select_by_visible_text(return_full_marital_status(appointment_data['marital_status']))

    have_expired_passport = Select(driver.find_element(By.ID, 'ddls_3'))
    have_expired_passport.select_by_visible_text(appointment_data['is_passport_expired'].capitalize())

    amount_minor_kids_input = driver.find_element(By.ID, 'DatiAddizionaliPrenotante_4___testo')
    amount_minor_kids_input.send_keys(appointment_data['amount_minor_kids'])


def complete_family_citizenship(driver, appointment_data):
    marital_status = Select(driver.find_element(By.ID, 'ddls_0'))
    marital_status.select_by_visible_text(return_full_marital_status(appointment_data['marital_status']))

    address_input = driver.find_element(By.ID, 'DatiAddizionaliPrenotante_1___testo')
    address_input.send_keys(appointment_data['address'])

    amount_minor_kids_input = driver.find_element(By.ID, 'DatiAddizionaliPrenotante_2___testo')
    amount_minor_kids_input.send_keys(appointment_data['amount_minor_kids'])


def sanitize_appointment_reason(appointment_reason):
    valid_reasons = {'Negocios', 'Tratamientos médicos', 'Competencia deportiva', 'Trabajo independiente',
                     'Trabajo subordinado', 'Misión', 'Motivos religiosos', 'Investigación', 'Estudio', 'Tránsito',
                     'Transporte', 'Turismo', 'Turista - Visita familiares/amigos', 'Reingresso', 'Altro'}
    if appointment_reason not in valid_reasons:
        raise Exception('Invalid appointment reason')

    return appointment_reason


def complete_visa_appointment(driver, appointment_data):
    # FIXME: Need to add multiple appointment support
    passport_expiry_date_input = driver.find_element(By.ID, 'DatiAddizionaliPrenotante_0___data')
    passport_expiry_date_input.click()
    passport_expiry_date_input.send_keys(appointment_data['passport_expiry_date'].split('/')[1])
    passport_expiry_date_input.send_keys(appointment_data['passport_expiry_date'].split('/')[0])
    passport_expiry_date_input.send_keys(appointment_data['passport_expiry_date'].split('/')[2])

    travel_reason = Select(driver.find_element(By.ID, 'ddls_1'))
    travel_reason.select_by_visible_text(sanitize_appointment_reason(appointment_data['travel_reason'].capitalize()))


def complete_appointment_details(driver, appointment_data):
    if appointment_data['appointment_type'] == 'PASAPORTE':
        # FIXME: This could also be an appointment for multiple people
        complete_passport_appointment_data(driver, appointment_data)
    if appointment_data['appointment_type'] == 'CIUDADANIA PADRES':
        complete_family_citizenship(driver, appointment_data)
    if appointment_data['appointment_type'] == 'VISADOS':
        complete_visa_appointment(driver, appointment_data)
    # There's no need for completing any data for descendent citizenship appointment


class NeedsRetryException(Exception):
    def __init__(self, message):
        self.message = message
