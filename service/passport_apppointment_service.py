from datetime import datetime

from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By

from config.config import settings as config_file
from helpers.logger import logger
from helpers.retry_function import retry_on_exception
from helpers.sanitizers import return_full_marital_status, return_full_parental_relationship
from helpers.save_html_content_to_file import save_html_content_to_file
from helpers.webdriver.find_element import find_element_by_xpath_and_click_it_with_javascript, \
    find_element_by_id_and_send_keys, find_element_by_id_and_click_it_with_javascript
from helpers.webdriver.select_element import select_element_by_visible_text_and_id
from helpers.webdriver.waits import wait_presence_of_element_located_by_id, wait_presence_of_element_located_by_xpath, \
    wait_visibility_of_element_located_by_xpath
from repositories.multiple_passport_appointment_repository import MultiplePassportAppointmentRepository
from service.database_service import DatabaseService
from webdrivers.webdriver import WebDriver


class PassportAppointmentService:
    def __init__(self, unlimited_wait):
        self.database_service = DatabaseService()
        self.appointment_repository = MultiplePassportAppointmentRepository()
        self.config = config_file.crawling
        self.driver = None
        self.unlimited_wait = unlimited_wait

    @retry_on_exception(5, retry_sleep_time=5)
    def schedule_passport_appointment_service(self, client_login_data, appointment_data):
        response = False
        try:
            # FIXME: We're using here general appointment_configs instead of passport_appointment_configs
            logger.info('Creating browser')
            self.driver = WebDriver().acquire(self.config.passport_appointment_controller.webdriver_type)

            self.driver.maximize_window()
            self.driver.get('https://prenotami.esteri.it/')
            self.log_in_user(client_login_data)
            logger.info('User logged in successfully')

            # Waiting for user area page to be fully loaded
            wait_presence_of_element_located_by_id(self.driver, 5, 'advanced', unlimited_wait=self.unlimited_wait,
                                                   message='Timeout waiting after login in user')
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
        wait_presence_of_element_located_by_id(self.driver, 5, 'login-email', unlimited_wait=self.unlimited_wait)
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Fill username input
        logger.info('Logging user {}'.format(client_login_data['username']))
        find_element_by_id_and_send_keys(self.driver, 'login-email', [client_login_data['username']])

        # Fill password input
        find_element_by_id_and_send_keys(self.driver, 'login-password', [client_login_data['password'], Keys.ENTER])

    @retry_on_exception(max_attempts=100, retry_sleep_time=5)
    def search_for_available_appointment(self, appointment_data):
        logger.info('Selecting appointment type passport')
        self.driver.get('https://prenotami.esteri.it/Services/Booking/104')
        self.raise_exception_on_non_available_appointment_warning_presence()

        # Saving html information in case anything fails we'll have a backup
        filename = 'passport_appointment_service_form#{}'.format(datetime.now().strftime("%Y-%m-%d"))
        save_html_content_to_file(self.driver.page_source, filename, 'html', '/tmp/prenotami-esteri/htmls')

        self.complete_appointment_data(appointment_data)

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
                if loop == 0:
                    # Saving html information in case anything fails we'll have a backup
                    filename = 'passport_appointment_service_form#{}'.format(datetime.now().strftime("%Y-%m-%d"))
                    save_html_content_to_file(self.driver.page_source, filename, 'html', '/tmp/prenotami-esteri/htmls')

                wait_presence_of_element_located_by_xpath(self.driver, 3, './/td[@class="day availableDay"]')
                # Click DAY with available appointments (day marked in green)
                logger.info('Available appointment found!')
                find_element_by_xpath_and_click_it_with_javascript(self.driver, './/td[@class="day availableDay"]')
                try:
                    # Select first available appointment
                    available_hours = self.driver.find_elements(By.XPATH, './/div[@class="dot "]')
                    if len(available_hours) > 0:
                        self.driver.execute_script("arguments[0].click();", available_hours[0])
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
        wait_visibility_of_element_located_by_xpath(self.driver, 5,
                                                    './/select[@id="typeofbookingddl"]/option[text()="Reserva multiple"]',
                                                    unlimited_wait=self.unlimited_wait)

        logger.info('Completing appointment data')
        # Select multiple appointment dropdown menu option
        find_element_by_id_and_send_keys(self.driver, 'typeofbookingddl', [Keys.ARROW_DOWN, 'Reserva multiple'])

        if len(appointment_data['additional_people_data']) > 4:
            raise Exception('Additional people amount cannot be greater than 4')

        # Open 'additional people' dropdown menu and select option
        wait_visibility_of_element_located_by_xpath(self.driver, 5,
                                                    './/select[@id="ddlnumberofcompanions"]/option[text()="{}"]'.format(
                                                        str(len(appointment_data['additional_people_data']))),
                                                    unlimited_wait=self.unlimited_wait)
        find_element_by_id_and_send_keys(self.driver, 'ddlnumberofcompanions', [Keys.ARROW_DOWN])
        select_element_by_visible_text_and_id(self.driver, 'ddlnumberofcompanions',
                                              str(len(appointment_data['additional_people_data'])))

        # Fill address input
        find_element_by_id_and_send_keys(self.driver, 'DatiAddizionaliPrenotante_0___testo',
                                         [appointment_data['address']])

        wait_visibility_of_element_located_by_xpath(self.driver, 5,
                                                    './/select[@id="ddls_1"]/option[text()="{}"]'.format(
                                                        appointment_data['have_kids'].capitalize()),
                                                    unlimited_wait=self.unlimited_wait,
                                                    message='Unable to locate have_kids selector')
        # Open 'have kids' dropdown menu and select option
        find_element_by_id_and_send_keys(self.driver, 'ddls_1', [Keys.ARROW_DOWN])
        select_element_by_visible_text_and_id(self.driver, 'ddls_1', appointment_data['have_kids'].capitalize())

        wait_visibility_of_element_located_by_xpath(self.driver, 5,
                                                    './/select[@id="ddls_2"]/option[text()="{}"]'.format(
                                                        return_full_marital_status(appointment_data['marital_status'])),
                                                    unlimited_wait=self.unlimited_wait)
        # Open 'marital status' dropdown menu and select option
        find_element_by_id_and_send_keys(self.driver, 'ddls_2', [Keys.ARROW_DOWN])
        select_element_by_visible_text_and_id(self.driver, 'ddls_2',
                                              return_full_marital_status(appointment_data['marital_status']))

        wait_visibility_of_element_located_by_xpath(self.driver, 5,
                                                    './/select[@id="ddls_3"]/option[text()="{}"]'.format(
                                                        appointment_data['own_expired_passport'].capitalize()),
                                                    unlimited_wait=self.unlimited_wait)
        # Open 'expired passport' dropdown menu and select option
        find_element_by_id_and_send_keys(self.driver, 'ddls_3', [Keys.ARROW_DOWN])
        select_element_by_visible_text_and_id(self.driver, 'ddls_3',
                                              appointment_data['own_expired_passport'].capitalize())

        # Fill minor kids amount input
        find_element_by_id_and_send_keys(self.driver, 'DatiAddizionaliPrenotante_4___testo',
                                         [appointment_data['minor_kids_amount']])

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

            wait_visibility_of_element_located_by_xpath(self.driver, 5,
                                                        './/select[@id="TypeOfRelationDDL{}"]/option[text()="{}"]'
                                                        .format(index, return_full_parental_relationship(
                                                            companion_data['relationship'])),
                                                        unlimited_wait=self.unlimited_wait)
            # Open 'parental relationship' dropdown menu and select option
            find_element_by_id_and_send_keys(self.driver, 'TypeOfRelationDDL{}'.format(index), [Keys.ARROW_DOWN])
            select_element_by_visible_text_and_id(self.driver, 'TypeOfRelationDDL{}'.format(index),
                                                  return_full_parental_relationship(companion_data['relationship']))

            wait_visibility_of_element_located_by_xpath(self.driver, 5,
                                                        './/select[@id="ddlsAcc_{}_0"]/option[text()="{}"]'
                                                        .format(index, companion_data['have_kids'].capitalize()),
                                                        unlimited_wait=self.unlimited_wait)
            # Open 'have kids' dropdwon menu and select option
            find_element_by_id_and_send_keys(self.driver, 'ddlsAcc_{}_0'.format(index), [Keys.ARROW_DOWN])
            select_element_by_visible_text_and_id(self.driver, 'ddlsAcc_{}_0'.format(index),
                                                  companion_data['have_kids'].capitalize())

            wait_visibility_of_element_located_by_xpath(self.driver, 5,
                                                        './/select[@id="ddlsAcc_{}_1"]/option[text()="{}"]'
                                                        .format(index, return_full_marital_status(
                                                            companion_data['marital_status'])),
                                                        unlimited_wait=self.unlimited_wait)
            # Open 'marital status' dropdown menu and select option
            find_element_by_id_and_send_keys(self.driver, 'ddlsAcc_{}_1'.format(index), [Keys.ARROW_DOWN])
            select_element_by_visible_text_and_id(self.driver, 'ddlsAcc_{}_1'.format(index),
                                                  return_full_marital_status(companion_data['marital_status']))

            # Fill address input
            find_element_by_id_and_send_keys(self.driver,
                                             'Accompagnatori_{}__DatiAddizionaliAccompagnatore_2___testo'.format(
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
            wait_presence_of_element_located_by_xpath(self.driver, 1,
                                                      './/div[text()="Al momento non ci sono date disponibili per il servizio richiesto"]')
            raise Exception('Non available appointments warning detected')
        except NoSuchElementException:
            pass

    def complete_appointment_data(self, appointment_data):
        if appointment_data.get('additional_people_data', None):
            if len(appointment_data.get('additional_people_data')) > 0:
                return self.complete_multiple_passport_appointment_data(appointment_data)

        return self.complete_simple_passport_appointment_data(appointment_data)

    def complete_simple_passport_appointment_data(self, appointment_data):
        # Waiting for appointment page to be fully loaded
        wait_visibility_of_element_located_by_xpath(self.driver, 5,
                                                    './/select[@id="typeofbookingddl"]/option[text()="Reserva multiple"]',
                                                    unlimited_wait=self.unlimited_wait)

        # Complete address information
        find_element_by_id_and_send_keys(self.driver, 'DatiAddizionaliPrenotante_0___testo',
                                         [appointment_data['address']])

        wait_visibility_of_element_located_by_xpath(self.driver, 5,
                                                    './/select[@id="ddls_1"]/option[text()="{}"]'.format(
                                                        appointment_data['have_kids'].capitalize()),
                                                    unlimited_wait=self.unlimited_wait)
        # Open 'Have kids' dropdown menu and select option
        find_element_by_id_and_send_keys(self.driver, 'ddls_1', [Keys.ARROW_DOWN])
        select_element_by_visible_text_and_id(self.driver, 'ddls_1', appointment_data['have_kids'].capitalize())

        wait_visibility_of_element_located_by_xpath(self.driver, 5,
                                                    './/select[@id="ddls_2"]/option[text()="{}"]'.format(
                                                        return_full_marital_status(appointment_data['marital_status'])),
                                                    unlimited_wait=self.unlimited_wait)
        # Open 'Marital status' dropdown menu and select option
        find_element_by_id_and_send_keys(self.driver, 'ddls_2', [Keys.ARROW_DOWN])
        select_element_by_visible_text_and_id(self.driver, 'ddls_2',
                                              return_full_marital_status(appointment_data['marital_status']))

        wait_visibility_of_element_located_by_xpath(self.driver, 5,
                                                    './/select[@id="ddls_3"]/option[text()="{}"]'.format(
                                                        appointment_data['is_passport_expired'].capitalize()),
                                                    unlimited_wait=self.unlimited_wait)
        # Open 'Expired passport' dropdown menu and select option
        find_element_by_id_and_send_keys(self.driver, 'ddls_3', [Keys.ARROW_DOWN])
        select_element_by_visible_text_and_id(self.driver, 'ddls_3',
                                              appointment_data['is_passport_expired'].capitalize())

        # Complete minor kids amount field
        find_element_by_id_and_send_keys(self.driver, 'DatiAddizionaliPrenotante_4___testo',
                                         [appointment_data['amount_minor_kids']])

