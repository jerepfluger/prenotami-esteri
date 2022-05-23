from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait

from config.config import settings as config_file
from dto.rest.login_credentials import LoginCredentials
from helpers.logger import logger
from helpers.retry_function import retry_on_exception
from helpers.sanitizers import return_full_marital_status, return_full_parental_relationship
from repositories.multiple_passport_appointment_repository import MultiplePassportAppointmentRepository
from service.database_service import DatabaseService
from webdrivers.webdriver import WebDriver


class PassportAppointmentService:
    def __init__(self):
        self.database_service = DatabaseService()
        self.appointment_repository = MultiplePassportAppointmentRepository()
        self.config = config_file.crawling
        self.driver = WebDriver().acquire(self.config.appointment_controller.webdriver_type)

    def schedule_multiple_passport_appointment(self, client_login_data, appointment_data):
        response = False
        try:
            self.driver.maximize_window()
            self.driver.get('https://prenotami.esteri.it/')
            self.log_in_user(client_login_data)

            # Waiting for user area page to be fully loaded
            WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.ID, 'advanced')))
            self.search_for_available_appointment(appointment_data)

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

    @retry_on_exception(5, retry_sleep_time=5)
    def log_in_user(self, client_login_data):
        # Waiting for login page to be fully loaded
        WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.ID, 'login-email')))
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # Complete username field
        logger.info('Logging user {}'.format(client_login_data['username']))
        username_input = self.driver.find_element(By.ID, 'login-email')
        username_input.send_keys(client_login_data['username'])
        # Complete password field
        password_input = self.driver.find_element(By.ID, 'login-password')
        password_input.send_keys(client_login_data['password'])
        password_input.send_keys(Keys.ENTER)

    @retry_on_exception(max_attempts=100, retry_sleep_time=5)
    def search_for_available_appointment(self, appointment_data):
        self.driver.get('https://prenotami.esteri.it/Language/ChangeLanguage?lang=13')
        WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.ID, 'advanced')))
        self.driver.get('https://prenotami.esteri.it/Services')

        # Waiting for prenotami tab to be fully loaded
        WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.ID, 'dataTableServices')))
        logger.info('Selecting appointment type passport')
        self.driver.get('https://prenotami.esteri.it/Services/Booking/104')

        logger.info('Completing appointment data')
        self.complete_multiple_passport_appointment_data(appointment_data)

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

    def complete_multiple_passport_appointment_data(self, appointment_data):
        # Waiting for appointment page to be fully loaded
        WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located(
            (By.XPATH, './/select[@id="typeofbookingddl"]/option[text()="Reserva multiple"]')))

        multiple_appointment_select = self.driver.find_element(By.ID, 'typeofbookingddl')
        multiple_appointment_select.send_keys(Keys.ARROW_DOWN)
        multiple_appointment_select.send_keys('Reserva multiple')

        if len(appointment_data['additional_people_data']) > 4:
            raise Exception('Additional people amount cannot be greater than 4')
        additional_people_input = self.driver.find_element(By.ID, 'ddlnumberofcompanions')
        additional_people_input.send_keys(Keys.ARROW_DOWN)
        additional_people_input = Select(self.driver.find_element(By.ID, 'ddlnumberofcompanions'))
        additional_people_input.select_by_visible_text(str(len(appointment_data['additional_people_data'])))

        address_input = self.driver.find_element(By.ID, 'DatiAddizionaliPrenotante_0___testo')
        address_input.send_keys(appointment_data['address'])

        # FIXME: We need to set a validator for this option
        WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located(
            (By.XPATH,
             './/select[@id="ddls_1"]/option[text()="{}"]'.format(appointment_data['have_kids'].capitalize()))),
            message='Unable to locate have_kids selector')
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
                 appointment_data['own_expired_passport'].capitalize()))))
        have_expired_passport_select = self.driver.find_element(By.ID, 'ddls_3')
        have_expired_passport_select.send_keys(Keys.ARROW_DOWN)
        have_expired_passport_select = Select(self.driver.find_element(By.ID, 'ddls_3'))
        have_expired_passport_select.select_by_visible_text(appointment_data['own_expired_passport'].capitalize())

        amount_minor_kids_input = self.driver.find_element(By.ID, 'DatiAddizionaliPrenotante_4___testo')
        amount_minor_kids_input.send_keys(appointment_data['minor_kids_amount'])

        for index, companion_data in enumerate(appointment_data['additional_people_data']):
            last_name_input = self.driver.find_element(By.ID,
                                                       'Accompagnatori_{}__CognomeAccompagnatore'.format(index))
            last_name_input.send_keys(companion_data['last_name'])

            first_name_input = self.driver.find_element(By.ID,
                                                        'Accompagnatori_{}__NomeAccompagnatore'.format(index))
            first_name_input.send_keys(companion_data['first_name'])

            birthdate_input = self.driver.find_element(By.ID,
                                                       'Accompagnatori_{}__DataNascitaAccompagnatore'.format(
                                                           index))
            birthdate_input.send_keys(companion_data['date_of_birth'])

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

    def save_multiple_passport_appointment(self, data):
        credentials = self.database_service.get_user_credentials(data.client_login['username'])
        if not credentials:
            credentials = self.database_service.save_new_credentials(data.client_login['username'], data.client_login['password'])
        return self.database_service.save_new_multiple_passport_appointment(credentials.id, data.client_appointment_data)
