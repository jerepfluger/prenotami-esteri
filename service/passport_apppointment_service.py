from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait

from config.config import settings as config_file
from helpers.logger import logger
from helpers.retry_function import retry_on_exception
from helpers.sanitizers import return_full_marital_status, return_full_parental_relationship
from helpers.webdriver.find_element import find_element_by_xpath_and_click_it_with_javascript, \
    find_element_by_id_and_send_keys, find_element_by_id_and_click_it_with_javascript
from helpers.webdriver.waits import wait_presence_of_element_located_by_id, wait_presence_of_element_located_by_xpath
from repositories.multiple_passport_appointment_repository import MultiplePassportAppointmentRepository
from service.database_service import DatabaseService
from webdrivers.webdriver import WebDriver


class PassportAppointmentService:
    def __init__(self):
        self.database_service = DatabaseService()
        self.appointment_repository = MultiplePassportAppointmentRepository()
        self.config = config_file.crawling
        self.driver = None

    def schedule_multiple_passport_appointment(self, client_login_data, appointment_data):
        response = False
        try:
            # FIXME: We're using here general appointment_configs instead of passport_appointment_configs
            logger.info('Creating browser')
            self.driver = WebDriver().acquire(self.config.appointment_controller.webdriver_type)
            self.driver.maximize_window()
            self.driver.get('https://prenotami.esteri.it/')
            self.log_in_user(client_login_data)
            logger.info('User logged in successfully')

            # Waiting for user area page to be fully loaded
            wait_presence_of_element_located_by_id(self.driver, 5, 'advanced', message='Timeout waiting after login in user')
            self.search_for_available_appointment(appointment_data)

            logger.info('Should be an available appointment. Start searching')
            self.select_available_appointment_or_raise_exception()

            # Click accept appointment button
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            find_element_by_xpath_and_click_it_with_javascript(self.driver, './/button[contains(text(), "Reservar")]')

            self.database_service.set_appointment_scheduled()
            # Accept and close
            wait_presence_of_element_located_by_id(self.driver, 5, 'btnStampa')

            # TODO: We need to save this to send it to the client
            self.driver.save_full_page_screenshot()

            response = True
        except Exception as ex:
            logger.exception(ex)
        finally:
            self.driver.close()
            self.driver.quit()
            logger.info('Webdriver fully destroyed')
            self.database_service.update_appointment_timestamp()

            return response

    @retry_on_exception(5, retry_sleep_time=5)
    def log_in_user(self, client_login_data):
        # Waiting for login page to be fully loaded
        wait_presence_of_element_located_by_id(self.driver, 5, 'login-email')
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Fill username input
        logger.info('Logging user {}'.format(client_login_data['username']))
        find_element_by_id_and_send_keys(self.driver, 'login-email', [client_login_data['username']])

        # Fill password input
        find_element_by_id_and_send_keys(self.driver, 'login-password', [client_login_data['password'], Keys.ENTER])

    @retry_on_exception(max_attempts=100, retry_sleep_time=5)
    def search_for_available_appointment(self, appointment_data):
        self.driver.get('https://prenotami.esteri.it/Language/ChangeLanguage?lang=13')
        wait_presence_of_element_located_by_id(self.driver, 5, 'advanced')
        self.driver.get('https://prenotami.esteri.it/Services')

        # Waiting for prenotami tab to be fully loaded
        wait_presence_of_element_located_by_id(self.driver, 5, 'dataTableServices')
        logger.info('Selecting appointment type passport')
        self.driver.get('https://prenotami.esteri.it/Services/Booking/104')
        self.raise_exception_on_non_available_appointment_warning_presence()

        logger.info('Completing appointment data')
        self.complete_multiple_passport_appointment_data(appointment_data)

        # Click privacy check button
        logger.info('Clicking privacy check box')
        find_element_by_id_and_click_it_with_javascript(self.driver, 'PrivacyCheck')

        # Click next button
        logger.info('Clicking next button to look for available appointment dates')
        find_element_by_id_and_click_it_with_javascript(self.driver, 'btnAvanti')

        self.driver.switch_to.alert.accept()

        logger.info('Data completition finished. Checking for available appointments')
        self.check_calendar_or_raise_exception()

    def select_available_appointment_or_raise_exception(self):
        loop = 0
        while True:
            if loop > 25:
                raise Exception('No appointments for next year')
            try:
                wait_presence_of_element_located_by_xpath(self.driver, 3, './/td[@class="day availableDay"]')
                # Click DAY with available appointments (day marked in green)
                logger.info('Available appointment found!')
                find_element_by_xpath_and_click_it_with_javascript(self.driver, './/td[@class="day availableDay"]')
                try:
                    # Select available appointment
                    find_element_by_xpath_and_click_it_with_javascript(self.driver, './/div[@class="dot "]')
                except NoSuchElementException:
                    pass
                break
            except TimeoutException:
                try:
                    logger.info('Looking for appointments on Next Month')
                    wait_presence_of_element_located_by_xpath(self.driver, 5, './/span[@title="Next Month"]')
                    # Click next month button
                    find_element_by_xpath_and_click_it_with_javascript(self.driver, './/span[@title="Next Month"]')
                    loop += 1
                except NoSuchElementException:
                    raise Exception('Unable to pick appointment')
                except TimeoutException:
                    raise Exception('Timeout waiting for click NextMonth button')

    def check_calendar_or_raise_exception(self):
        try:
            wait_presence_of_element_located_by_xpath(self.driver, 5, './/section[@class="calendario"]')
        except TimeoutException:
            try:
                # Click OK button
                find_element_by_xpath_and_click_it_with_javascript(self.driver, './/button[@class="btn btn-blue"]')
            except NoSuchElementException:
                pass
            logger.info('No appointments available')
            raise Exception('No available appointments')

    def complete_multiple_passport_appointment_data(self, appointment_data):
        # Waiting for appointment page to be fully loaded
        WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located(
            (By.XPATH, './/select[@id="typeofbookingddl"]/option[text()="Reserva multiple"]')))

        # Select multiple appointment dropdown menu option
        find_element_by_id_and_send_keys(self.driver, 'typeofbookingddl', [Keys.ARROW_DOWN, 'Reserva multiple'])

        if len(appointment_data['additional_people_data']) > 4:
            raise Exception('Additional people amount cannot be greater than 4')

        # Open 'additional people' dropdown menu
        find_element_by_id_and_send_keys(self.driver, 'ddlnumberofcompanions', [Keys.ARROW_DOWN])
        # FIXME: Here I should have a new method which allows me to use 'Select' functionality
        additional_people_input = Select(self.driver.find_element(By.ID, 'ddlnumberofcompanions'))
        additional_people_input.select_by_visible_text(str(len(appointment_data['additional_people_data'])))

        # Fill address input
        find_element_by_id_and_send_keys(self.driver, 'DatiAddizionaliPrenotante_0___testo', [appointment_data['address']])

        # FIXME: We need to set a validator for this option
        WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located(
            (By.XPATH,
             './/select[@id="ddls_1"]/option[text()="{}"]'.format(appointment_data['have_kids'].capitalize()))),
            message='Unable to locate have_kids selector')
        # Open 'have kids' dropdown menu
        find_element_by_id_and_send_keys(self.driver, 'ddls_1', [Keys.ARROW_DOWN])
        # FIXME: Here I should have a new method which allows me to use 'Select' functionality
        have_kids_select = Select(self.driver.find_element(By.ID, 'ddls_1'))
        have_kids_select.select_by_visible_text(appointment_data['have_kids'].capitalize())

        WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located(
            (By.XPATH, './/select[@id="ddls_2"]/option[text()="{}"]'.format(
                return_full_marital_status(appointment_data['marital_status'])))))
        # Open 'marital status' dropdown menu
        find_element_by_id_and_send_keys(self.driver, 'ddls_2', [Keys.ARROW_DOWN])
        # FIXME: Here I should have a new method which allows me to use 'Select' functionality
        marital_status_select = Select(self.driver.find_element(By.ID, 'ddls_2'))
        marital_status_select.select_by_visible_text(return_full_marital_status(appointment_data['marital_status']))

        WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located(
            (By.XPATH,
             './/select[@id="ddls_3"]/option[text()="{}"]'.format(
                 appointment_data['own_expired_passport'].capitalize()))))
        # Open 'expired passport' dropdown menu
        find_element_by_id_and_send_keys(self.driver, 'ddls_3', [Keys.ARROW_DOWN])
        # FIXME: Here I should have a new method which allows me to use 'Select' functionality
        have_expired_passport_select = Select(self.driver.find_element(By.ID, 'ddls_3'))
        have_expired_passport_select.select_by_visible_text(appointment_data['own_expired_passport'].capitalize())

        # Fill minor kids amount input
        find_element_by_id_and_send_keys(self.driver, 'DatiAddizionaliPrenotante_4___testo', [appointment_data['minor_kids_amount']])

        for index, companion_data in enumerate(appointment_data['additional_people_data']):
            # Fill lastname input
            find_element_by_id_and_send_keys(self.driver, 'Accompagnatori_{}__CognomeAccompagnatore'.format(index),
                                             [companion_data['last_name']])
            # Fill first name input
            find_element_by_id_and_send_keys(self.driver, 'Accompagnatori_{}__NomeAccompagnatore'.format(index),
                                             [companion_data['first_name']])
            # Fill birthdate input
            find_element_by_id_and_send_keys(self.driver, 'Accompagnatori_{}__DataNascitaAccompagnatore'.format(index),
                                             [companion_data['date_of_birth']])

            WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located(
                (By.XPATH, './/select[@id="TypeOfRelationDDL{}"]/option[text()="{}"]'
                 .format(index, return_full_parental_relationship(companion_data['relationship'])))))
            # Open 'parental relationship' dropdown menu
            find_element_by_id_and_send_keys(self.driver, 'TypeOfRelationDDL{}'.format(index), [Keys.ARROW_DOWN])
            # FIXME: Here I should have a new method which allows me to use 'Select' functionality
            parental_relationship_select = Select(
                self.driver.find_element(By.ID, 'TypeOfRelationDDL{}'.format(index)))
            parental_relationship_select.select_by_visible_text(
                return_full_parental_relationship(companion_data['relationship']))

            WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located(
                (By.XPATH, './/select[@id="ddlsAcc_{}_0"]/option[text()="{}"]'
                 .format(index, companion_data['have_kids'].capitalize()))))
            # Open 'have kids' dropdwon menu
            find_element_by_id_and_send_keys(self.driver, 'ddlsAcc_{}_0'.format(index), [Keys.ARROW_DOWN])
            # FIXME: Here I should have a new method which allows me to use 'Select' functionality
            have_kids_select = Select(self.driver.find_element(By.ID, 'ddlsAcc_{}_0'.format(index)))
            have_kids_select.select_by_visible_text(companion_data['have_kids'].capitalize())

            WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located(
                (By.XPATH, './/select[@id="ddlsAcc_{}_1"]/option[text()="{}"]'
                 .format(index, return_full_marital_status(companion_data['marital_status'])))))
            # Open 'marital status' dropdown menu
            find_element_by_id_and_send_keys(self.driver, 'ddlsAcc_{}_1'.format(index), [Keys.ARROW_DOWN])
            # FIXME: Here I should have a new method which allows me to use 'Select' functionality
            marital_status_select = Select(self.driver.find_element(By.ID, 'ddlsAcc_{}_1'.format(index)))
            marital_status_select.select_by_visible_text(
                return_full_marital_status(companion_data['marital_status']))

            # Fill address input
            find_element_by_id_and_send_keys(self.driver, 'Accompagnatori_{}__DatiAddizionaliAccompagnatore_2___testo'.format(
                                                         index), [companion_data['address']])

    def save_multiple_passport_appointment(self, data):
        credentials = self.database_service.get_user_credentials(data.client_login['username'])
        if not credentials:
            credentials = self.database_service.save_new_credentials(data.client_login['username'],
                                                                     data.client_login['password'])
        return self.database_service.save_new_multiple_passport_appointment(credentials.id,
                                                                            data.client_appointment_data)

    def raise_exception_on_non_available_appointment_warning_presence(self):
        try:
            self.driver.find_element(By.XPATH, './/div[text()="Al momento non ci sono date disponibili per il servizio richiesto"]')
            raise Exception('Non available appointments warning detected')
        except NoSuchElementException:
            pass
