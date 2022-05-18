import time

from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait

from config.config import settings as config_file
from helpers.logger import logger
from helpers.retry_function import retry_on_exception
from repositories.appointment_repository import AppointmentRepository
from service.database_service import DatabaseService
from webdrivers.webdriver import WebDriver


class AppointmentService:
    def __init__(self):
        self.database_service = DatabaseService()
        self.appointment_repository = AppointmentRepository()
        self.config = config_file.crawling
        self.driver = WebDriver().acquire(self.config.appointment_controller.webdriver_type)

    def schedule_generic_appointment(self, appointment_data):
        response = False
        try:
            self.driver.maximize_window()
            self.driver.get('https://prenotami.esteri.it/')
            self.log_in_user(appointment_data)

            # Waiting for user area page to be fully loaded
            WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.ID, 'advanced')))
            self.search_for_available_appointment(appointment_data, self.driver)

            logger.info('Should be an available appointment. Start searching')
            self.select_available_appointment_or_raise_exception()

            # Accept appointment
            accept_appointment_button = self.driver.find_element(By.ID, 'btnPrenotaNoOtp')
            self.driver.execute_script("arguments[0].click();", accept_appointment_button)

            self.database_service.set_appointment_scheduled()
            # Accept and close
            WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.ID, 'btnStampa')))

            # TODO: We need to save this to send it to the client
            self.driver.save_full_page_screenshot()

            response = True
        except Exception as ex:
            logger.exception(ex)
            try:
                self.driver.close()
                self.driver.quit()
            except NameError:
                pass
            logger.info('Webdriver fully destroyed')
        finally:
            self.database_service.update_appointment_timestamp()
            return response

    def schedule_multiple_appointment(self, appointment_data):
        pass

    @retry_on_exception(5, retry_sleep_time=5)
    def log_in_user(self, appointment_data):
        # Waiting for login page to be fully loaded
        WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.ID, 'login-email')))
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # Complete username field
        logger.info('Logging user {}'.format(appointment_data['username'].split('@')[0]))
        username_input = self.driver.find_element(By.ID, 'login-email')
        username_input.send_keys(appointment_data['username'])
        # Complete password field
        password_input = self.driver.find_element(By.ID, 'login-password')
        password_input.send_keys(appointment_data['password'])
        password_input.send_keys(Keys.ENTER)

    @retry_on_exception(max_attempts=100, retry_sleep_time=5)
    def search_for_available_appointment(self, appointment_data):
        self.driver.get('https://prenotami.esteri.it/Language/ChangeLanguage?lang=13')
        WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.ID, 'advanced')))
        self.driver.get('https://prenotami.esteri.it/Services')

        # Waiting for prenotami tab to be fully loaded
        WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.ID, 'dataTableServices')))
        logger.info('Selecting appointment type {}'.format(appointment_data['appointment_type']))
        self.redirect_to_appointment_page(appointment_data['appointment_type'])

        logger.info('Completing appointment data')
        self.complete_appointment_details(appointment_data)

        privacy_check_box = self.driver.find_element(By.ID, 'PrivacyCheck')
        self.driver.execute_script("arguments[0].click();", privacy_check_box)

        next_button = self.driver.find_element(By.ID, 'btnAvanti')
        self.driver.execute_script("arguments[0].click();", next_button)

        self.driver.switch_to.alert.accept()

        logger.info('Data completition finished. Checking for available appointments')
        self.check_calendar_or_raise_exception()

    def select_available_appointment_or_raise_exception(self):
        loop = 0
        while True:
            if loop > 11:
                raise Exception('No appointments for next year')
            try:
                WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.XPATH, './/td[@class="day availableDay"]')))
                logger.info('Available appointment found!')
                available_date = self.driver.find_element(By.XPATH, './/td[@class="day availableDay"]')
                self.driver.execute_script("arguments[0].click();", available_date)
                break
            except TimeoutException:
                try:
                    logger.info('Looking for appointments on Next Month')
                    WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, './/span[@title="Next Month"]')))
                    next_month_button = self.driver.find_element(By.XPATH, './/span[@title="Next Month"]')
                    self.driver.execute_script("arguments[0].click();", next_month_button)
                    loop += 1
                except NoSuchElementException:
                    raise Exception('Unable to pick appointment')
                except TimeoutException:
                    raise Exception('Timeout waiting for click NextMonth button')

    def check_calendar_or_raise_exception(self):
        try:
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, './/section[@class="calendario"]')))
        except TimeoutException:
            try:
                ok_button = self.driver.find_element(By.XPATH, './/button[@class="btn btn-blue"]')
                self.driver.execute_script("arguments[0].click();", ok_button)
            except NoSuchElementException:
                pass
            logger.info('No appointments available')
            raise Exception('No available appointments')

    # TODO: Maybe we could add new appointment types
    # FIXME: There needs to be an appointment validator. Not every appointment is available for any city
    def redirect_to_appointment_page(self, appointment_type):
        if appointment_type == 'PASAPORTE':
            return self.driver.get('https://prenotami.esteri.it/Services/Booking/104')
        if appointment_type == 'CIUDADANIA DESCENDENCIA':
            return self.driver.get('https://prenotami.esteri.it/Services/Booking/340')
        if appointment_type == 'CIUDADANIA PADRES':
            return self.driver.get('https://prenotami.esteri.it/Services/Booking/339')
        if appointment_type == 'VISADOS':
            return self.driver.get('https://prenotami.esteri.it/Services/Booking/753')
        if appointment_type == 'CARTA DE IDENTIDAD':
            return self.driver.get('https://prenotami.esteri.it/Services/Booking/645')
        raise Exception('Unknown appointment type')

    def complete_passport_appointment_data(self, appointment_data):
        # Waiting for appointment page to be fully loaded
        WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located(
            (By.XPATH, './/select[@id="typeofbookingddl"]/option[text()="Reserva multiple"]')))

        if appointment_data.get('multiple_appointment'):
            multiple_appointment_select = self.driver.find_element(By.ID, 'typeofbookingddl')
            multiple_appointment_select.send_keys(Keys.ARROW_DOWN)
            multiple_appointment_select.send_keys('Reserva multiple')

            if appointment_data['additional_people_amount'] > 4:
                raise Exception('Additional people amount cannot be greater than 4')
            additional_people_input = self.driver.find_element(By.ID, 'ddlnumberofcompanions')
            additional_people_input.send_keys(Keys.ARROW_DOWN)
            additional_people_input = Select(self.driver.find_element(By.ID, 'ddlnumberofcompanions'))
            additional_people_input.select_by_visible_text(str(appointment_data['additional_people_amount']))

        address_input = self.driver.find_element(By.ID, 'DatiAddizionaliPrenotante_0___testo')
        address_input.send_keys(appointment_data['address'])

        # FIXME: We need to set a validator for this option
        WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located(
            (By.XPATH,
             './/select[@id="ddls_1"]/option[text()="{}"]'.format(appointment_data['have_kids'].capitalize()))))
        have_kids_select = self.driver.find_element(By.ID, 'ddls_1')
        have_kids_select.send_keys(Keys.ARROW_DOWN)
        have_kids_select = Select(self.driver.find_element(By.ID, 'ddls_1'))
        have_kids_select.select_by_visible_text(appointment_data['have_kids'].capitalize())

        WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located(
            (By.XPATH, './/select[@id="ddls_2"]/option[text()="{}"]'.format(
                return_full_marital_status(appointment_data['marital_status'])))))
        marital_status_select = self.driver.find_element(By.ID, 'ddls_2')
        marital_status_select.send_keys(Keys.ARROW_DOWN)
        marital_status_select = Select(self.driver.find_element(By.ID, 'ddls_2'))
        marital_status_select.select_by_visible_text(return_full_marital_status(appointment_data['marital_status']))

        WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located(
            (By.XPATH,
             './/select[@id="ddls_3"]/option[text()="{}"]'.format(
                 appointment_data['is_passport_expired'].capitalize()))))
        have_expired_passport_select = self.driver.find_element(By.ID, 'ddls_3')
        have_expired_passport_select.send_keys(Keys.ARROW_DOWN)
        have_expired_passport_select = Select(self.driver.find_element(By.ID, 'ddls_3'))
        have_expired_passport_select.select_by_visible_text(appointment_data['is_passport_expired'].capitalize())

        amount_minor_kids_input = self.driver.find_element(By.ID, 'DatiAddizionaliPrenotante_4___testo')
        amount_minor_kids_input.send_keys(appointment_data['amount_minor_kids'])

        if appointment_data.get('multiple_appointment'):
            for index, companion_data in enumerate(appointment_data['additional_people_data']):
                last_name_input = self.driver.find_element(By.ID,
                                                           'Accompagnatori_{}__CognomeAccompagnatore'.format(index))
                last_name_input.send_keys(companion_data['last_name'])

                first_name_input = self.driver.find_element(By.ID,
                                                            'Accompagnatori_{}__NomeAccompagnatore'.format(index))
                first_name_input.send_keys(companion_data['first_name'])

                birthdate_input = self.driver.find_element(By.ID,
                                                           'Accompagnatori_{}__DataNascitaAccompagnatore'.format(index))
                birthdate_input.send_keys(companion_data['birthdate'])

                WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located(
                    (By.XPATH, './/select[@id="TypeOfRelationDDL{}"]/option[text()="{}"]'
                     .format(index, return_full_parental_relationship(companion_data['relationship'])))))
                parental_relationship_select = self.driver.find_element(By.ID, 'TypeOfRelationDDL{}'.format(index))
                parental_relationship_select.send_keys(Keys.ARROW_DOWN)
                parental_relationship_select = Select(
                    self.driver.find_element(By.ID, 'TypeOfRelationDDL{}'.format(index)))
                parental_relationship_select.select_by_visible_text(
                    return_full_parental_relationship(companion_data['relationship']))

                WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located(
                    (By.XPATH, './/select[@id="ddlsAcc_{}_0"]/option[text()="{}"]'
                     .format(index, companion_data['have_kids'].capitalize()))))
                have_kids_select = self.driver.find_element(By.ID, 'ddlsAcc_{}_0'.format(index))
                have_kids_select.send_keys(Keys.ARROW_DOWN)
                have_kids_select = Select(self.driver.find_element(By.ID, 'ddlsAcc_{}_0'.format(index)))
                have_kids_select.select_by_visible_text(companion_data['have_kids'].capitalize())

                WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located(
                    (By.XPATH, './/select[@id="ddlsAcc_{}_1"]/option[text()="{}"]'
                     .format(index, return_full_marital_status(companion_data['marital_status'])))))
                marital_status_select = self.driver.find_element(By.ID, 'ddlsAcc_{}_1'.format(index))
                marital_status_select.send_keys(Keys.ARROW_DOWN)
                marital_status_select = Select(self.driver.find_element(By.ID, 'ddlsAcc_{}_1'.format(index)))
                marital_status_select.select_by_visible_text(
                    return_full_marital_status(companion_data['marital_status']))

                address_input = self.driver.find_element(By.ID,
                                                         'Accompagnatori_{}__DatiAddizionaliAccompagnatore_2___testo'.format(
                                                             index))
                address_input.send_keys(companion_data['address'])

    def complete_family_citizenship_data(self, appointment_data):
        marital_status = Select(self.driver.find_element(By.ID, 'ddls_0'))
        marital_status.select_by_visible_text(return_full_marital_status(appointment_data['marital_status']))

        address_input = self.driver.find_element(By.ID, 'DatiAddizionaliPrenotante_1___testo')
        address_input.send_keys(appointment_data['address'])

        amount_minor_kids_input = self.driver.find_element(By.ID, 'DatiAddizionaliPrenotante_2___testo')
        amount_minor_kids_input.send_keys(appointment_data['amount_minor_kids'])

    def complete_visa_appointment_data(self, appointment_data):
        # FIXME: Need to add multiple appointment support
        passport_expiry_date_input = self.driver.find_element(By.ID, 'DatiAddizionaliPrenotante_0___data')
        # Format need to be "yyyy-mm-dd"
        passport_expiry_date_input.send_keys(appointment_data['passport_expiry_date'])

        travel_reason = Select(self.driver.find_element(By.ID, 'ddls_1'))
        travel_reason.select_by_visible_text(
            sanitize_appointment_reason(appointment_data['travel_reason'].capitalize()))

    def complete_id_card_data(self, appointment_data):
        # FIXME: Need to add multiple appointment support
        address_input = self.driver.find_element(By.ID, 'DatiAddizionaliPrenotante_0___testo')
        address_input.send_keys(appointment_data['address'])
        have_kids_select = Select(self.driver.find_element(By.ID, 'ddls_1'))
        time.sleep(0.1)
        have_kids_select.select_by_visible_text(appointment_data['have_kids'].capitalize())
        amount_minor_kids_input = self.driver.find_element(By.ID, 'DatiAddizionaliPrenotante_2___testo')
        amount_minor_kids_input.send_keys(appointment_data['amount_minor_kids'])
        height_input = self.driver.find_element(By.ID, 'DatiAddizionaliPrenotante_3___testo')
        height_input.send_keys(appointment_data['height'])
        zip_code_input = self.driver.find_element(By.ID, 'DatiAddizionaliPrenotante_4___testo')
        zip_code_input.send_keys(appointment_data['zip_code'])
        other_citizenships_input = self.driver.find_element(By.ID, 'DatiAddizionaliPrenotante_5___testo')
        other_citizenships_input.send_keys(appointment_data['other_citizenships'].capitalize())
        marital_status_input = Select(self.driver.find_element(By.ID, 'ddls_6'))
        marital_status_input.select_by_visible_text(return_full_marital_status(appointment_data['marital_status']))

    def complete_appointment_details(self, appointment_data):
        if appointment_data['appointment_type'] == 'PASAPORTE':
            self.complete_passport_appointment_data(appointment_data)
        if appointment_data['appointment_type'] == 'CIUDADANIA PADRES':
            self.complete_family_citizenship_data(appointment_data)
        if appointment_data['appointment_type'] == 'VISADOS':
            self.complete_visa_appointment_data(appointment_data)
        if appointment_data['appointment_type'] == 'CARTA DE IDENTIDAD':
            self.complete_id_card_data(appointment_data)
        # There's no need for completing any data for descendent citizenship appointment


def return_full_marital_status(marital_status):
    marital_status = marital_status.upper()
    if marital_status == 'CASADO' or marital_status == 'CASADA' or marital_status == 'CASADO/A':
        return 'Casado/a'
    if marital_status == 'DIVORCIADO' or marital_status == 'DIVORCIADA' or marital_status == 'DIVORCIADO/A':
        return 'Divorciado/a'
    if marital_status == 'VIUDO' or marital_status == 'VIUDA' or marital_status == 'VIUDO/A':
        return 'Viudo/a'
    if marital_status == 'SOLTERO' or marital_status == 'SOLTERA' or marital_status == 'SOLTERO/A':
        return 'Soltero/a'
    if marital_status == 'SEPARADO' or marital_status == 'SEPARADA' or marital_status == 'SEPARADO/A':
        return 'Separado/a'
    if marital_status == 'UNION CIVIL':
        return 'Unido/a civilmente'
    if marital_status == 'SEPARADO U/C' or marital_status == 'SEPARADA U/C' or marital_status == 'SEPARADO/A U/C':
        return 'Separado/a de Un. Civ.'
    if marital_status == 'DIVORCIADO U/C' or marital_status == 'DIVORCIADA U/C' or marital_status == 'DIVORCIADO/A U/C':
        return 'Divorciado/a de Un. Civ.'
    if marital_status == 'VIUDO U/C' or marital_status == 'VIUDA U/C' or marital_status == 'VIUDO/A U/C':
        return 'Viudo/a de Un. Civ.'
    raise Exception('Marital status not present in Prenotami availability list')


def return_full_parental_relationship(parental_relationship):
    if parental_relationship == 'Concubino':
        return 'Concubino'
    if parental_relationship == 'Conyuge':
        return 'Conyuge'
    if parental_relationship == 'Conyuge divorciado':
        return 'Conyuge divorciado'
    if parental_relationship == 'Conyuge separado':
        return 'Conyuge separado'
    if parental_relationship == 'Hermano' or parental_relationship == 'Hermana' or parental_relationship == 'Hermano/Hermana':
        return 'Hermano/Hermana'
    if parental_relationship == 'Hijo de otro conyuge':
        return 'Hijo de otro conyuge'
    if parental_relationship == 'Hijo' or parental_relationship == 'Hija' or parental_relationship == 'Hijo/a':
        return 'Hijo/a'
    if parental_relationship == 'Menor en tenencia':
        return 'Menor en tenencia'
    if parental_relationship == 'Nieto':
        return 'Nieto'
    if parental_relationship == 'Padre' or parental_relationship == 'Madre' or parental_relationship == 'Padre/Madre':
        return 'Padre/Madre'
    if parental_relationship == 'Suegro' or parental_relationship == 'Suegra' or parental_relationship == 'Suegro/Suegra':
        return 'Suegro/Suegra'
    if parental_relationship == 'Yerno' or parental_relationship == 'Nuera' or parental_relationship == 'Yerno/Nuera':
        return 'Yerno/Nuera'
    raise Exception('Parental relationship not present in Prenotami availability list')


def sanitize_appointment_reason(appointment_reason):
    valid_reasons = {'Negocios', 'Tratamientos médicos', 'Competencia deportiva', 'Trabajo independiente',
                     'Trabajo subordinado', 'Misión', 'Motivos religiosos', 'Investigación', 'Estudio', 'Tránsito',
                     'Transporte', 'Turismo', 'Turista - Visita familiares/amigos', 'Reingresso', 'Altro'}
    if appointment_reason not in valid_reasons:
        raise Exception('Invalid appointment reason')

    return appointment_reason
