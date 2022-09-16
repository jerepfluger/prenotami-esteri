import time
from datetime import datetime

from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select

from config.config import settings as config_file
from helpers.logger import logger
from helpers.retry_function import retry_on_exception
from helpers.sanitizers import return_full_marital_status, return_full_parental_relationship, \
    sanitize_appointment_reason
from helpers.save_html_content_to_file import save_html_content_to_file
from helpers.webdriver.find_element import find_element_by_xpath_and_click_it_with_javascript, \
    find_element_by_id_and_send_keys, find_element_by_id_and_click_it_with_javascript
from helpers.webdriver.select_element import select_element_by_visible_text_and_id
from helpers.webdriver.waits import wait_presence_of_element_located_by_id, wait_presence_of_element_located_by_xpath, \
    wait_visibility_of_element_located_by_xpath
from repositories.appointment_repository import AppointmentRepository
from service.database_service import DatabaseService
from webdrivers.webdriver import WebDriver


class AppointmentService:
    def __init__(self, unlimited_wait=False):
        self.database_service = DatabaseService()
        self.appointment_repository = AppointmentRepository()
        self.config = config_file.crawling
        self.driver = None
        self.unlimited_wait = unlimited_wait

    def schedule_generic_appointment(self, appointment_data):
        response = False
        try:
            self.driver = WebDriver().acquire(self.config.appointment_controller.webdriver_type)
            self.driver.maximize_window()
            self.driver.get('https://prenotami.esteri.it/')
            self.log_in_user(appointment_data)

            # Waiting for user area page to be fully loaded
            wait_presence_of_element_located_by_id(self.driver, 5, 'advanced', self.unlimited_wait)
            self.search_for_available_appointment(appointment_data)

            logger.info('Should be an available appointment. Start searching')
            self.select_available_appointment_or_raise_exception()

            # Accept appointment
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # Click accept appointment button
            find_element_by_xpath_and_click_it_with_javascript(self.driver, './/button[contains(text(), "Reservar")]')

            self.database_service.set_appointment_scheduled()
            # Accept and close
            wait_presence_of_element_located_by_id(self.driver, 5, 'btnStampa', self.unlimited_wait)

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

    def schedule_multiple_appointment(self, appointment_data):
        pass

    @retry_on_exception(5, retry_sleep_time=5)
    def log_in_user(self, appointment_data):
        # Waiting for login page to be fully loaded
        wait_presence_of_element_located_by_id(self.driver, 5, 'login-email', unlimited_wait=self.unlimited_wait,
                                               message='Unable to locate email input text')
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Complete username field
        logger.info('Logging user {}'.format(appointment_data['username'].split('@')[0]))
        find_element_by_id_and_send_keys(self.driver, 'login-email', [appointment_data['username']])

        # Complete password field
        find_element_by_id_and_send_keys(self.driver, 'login-password', [appointment_data['password'], Keys.ENTER])

    @retry_on_exception(max_attempts=100, retry_sleep_time=5)
    def search_for_available_appointment(self, appointment_data):
        logger.info('Selecting appointment type {}'.format(appointment_data['appointment_type']))
        self.redirect_to_appointment_page(appointment_data['appointment_type'])
        self.raise_exception_on_non_available_appointment_warning_presence()

        # Saving html information in case anything fails we'll have a backup
        # filename = 'appointment_service_form#{}#{}'.format(appointment_data['appointment_type'], datetime.now().strftime("%Y-%m-%d"))
        # save_html_content_to_file(self.driver.page_source, filename, 'html', '/tmp/prenotami-esteri/htmls')

        logger.info('Completing appointment data')
        self.complete_appointment_details(appointment_data)

        # Click privacy checkbox
        find_element_by_id_and_click_it_with_javascript(self.driver, 'PrivacyCheck')

        # Click next button
        find_element_by_id_and_click_it_with_javascript(self.driver, 'btnAvanti')

        self.driver.switch_to.alert.accept()

        logger.info('Data completition finished. Checking for available appointments')
        self.check_calendar_or_raise_exception()

    def select_available_appointment_or_raise_exception(self):
        loop = 0
        while True:
            if loop > 25:
                raise Exception('No appointments for next two years')
            try:
                # Saving html information in case anything fails we'll have a backup
                if loop == 0:
                    filename = 'appointment_service_calendar#{}'.format(datetime.now().strftime("%Y-%m-%d"))
                    save_html_content_to_file(self.driver.page_source, filename, 'html', '/tmp/prenotami-esteri/htmls')

                wait_presence_of_element_located_by_xpath(self.driver, 3, './/td[@class="day availableDay"]', self.unlimited_wait)
                logger.info('Available appointment found!')
                # Click DAY with available appointments (day marked in green)
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
                    wait_presence_of_element_located_by_xpath(self.driver, 5, './/span[@title="Next Month"]', self.unlimited_wait)
                    # Click next month button
                    find_element_by_xpath_and_click_it_with_javascript(self.driver, './/span[@title="Next Month"]')
                    loop += 1
                except NoSuchElementException:
                    raise Exception('Unable to pick appointment')
                except TimeoutException:
                    raise Exception('Timeout waiting for click NextMonth button')

    def check_calendar_or_raise_exception(self):
        try:
            wait_presence_of_element_located_by_xpath(self.driver, 5, './/section[@class="calendario"]', self.unlimited_wait)
        except TimeoutException:
            try:
                # Click ok button
                find_element_by_xpath_and_click_it_with_javascript(self.driver, './/button[@class="btn btn-blue"]')
            except NoSuchElementException:
                pass
            logger.info('No appointments available')
            raise Exception('No available appointments')

    # TODO: There needs to be an appointment validator. Not every appointment is available for any city
    def redirect_to_appointment_page(self, appointment_type):
        appointment_type = appointment_type.upper()
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
        wait_visibility_of_element_located_by_xpath(self.driver, 5,
                                                    './/select[@id="typeofbookingddl"]/option[text()="Reserva multiple"]',
                                                    unlimited_wait=self.unlimited_wait)

        if appointment_data.get('multiple_appointment', False):
            # Select 'Reserva multiple' from dropdown menu
            find_element_by_id_and_send_keys(self.driver, 'typeofbookingddl', [Keys.ARROW_DOWN, 'Reserva multiple'])

            if appointment_data['additional_people_amount'] > 4:
                raise Exception('Additional people amount cannot be greater than 4')

            # Select amount of additional people
            find_element_by_id_and_send_keys(self.driver, 'ddlnumberofcompanions', [Keys.ARROW_DOWN])
            select_element_by_visible_text_and_id(self.driver, 'ddlnumberofcompanions',
                                                  str(appointment_data['additional_people_amount']))

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

        if appointment_data.get('multiple_appointment'):
            for index, companion_data in enumerate(appointment_data['additional_people_data']):
                # Fill lastname input
                find_element_by_id_and_send_keys(self.driver, 'Accompagnatori_{}__CognomeAccompagnatore'.format(index),
                                                 [companion_data['last_name']])
                # Fill first name input
                find_element_by_id_and_send_keys(self.driver, 'Accompagnatori_{}__NomeAccompagnatore'.format(index),
                                                 [companion_data['first_name']])
                # Fill birthday input
                find_element_by_id_and_send_keys(self.driver,
                                                 'Accompagnatori_{}__DataNascitaAccompagnatore'.format(index),
                                                 [companion_data['birthdate']])

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
                # Open 'have kids' dropdown menu and select option
                find_element_by_id_and_send_keys(self.driver, 'ddlsAcc_{}_0'.format(index), [Keys.ARROW_DOWN])
                select_element_by_visible_text_and_id(self.driver, 'ddlsAcc_{}_0'.format(index),
                                                      companion_data['have_kids'].capitalize())

                wait_visibility_of_element_located_by_xpath(self.driver, 5,
                                                            './/select[@id="ddlsAcc_{}_1"]/option[text()="{}"]'
                                                            .format(index, return_full_marital_status(
                                                                companion_data['marital_status'])),
                                                            unlimited_wait=self.unlimited_wait)
                # Open 'marital status' dropdown menu
                find_element_by_id_and_send_keys(self.driver, 'ddlsAcc_{}_1'.format(index), [Keys.ARROW_DOWN])
                select_element_by_visible_text_and_id(self.driver, 'ddlsAcc_{}_1'.format(index),
                                                      return_full_marital_status(companion_data['marital_status']))

                # Fill address input
                find_element_by_id_and_send_keys(self.driver,
                                                 'Accompagnatori_{}__DatiAddizionaliAccompagnatore_2___testo'.format(
                                                     index),
                                                 [companion_data['address']])

    def complete_family_citizenship_data(self, appointment_data):
        # FIXME: Should I add any logic before clicking here ?
        # marital_status = Select(self.driver.find_element(By.ID, 'ddls_0'))
        # marital_status.select_by_visible_text(return_full_marital_status(appointment_data['marital_status']))
        #
        # # Fill address input
        # find_element_by_id_and_send_keys(self.driver, 'DatiAddizionaliPrenotante_1___testo',
        #                                  [appointment_data['address']])
        #
        # # Fill minor kids amount input
        # find_element_by_id_and_send_keys(self.driver, 'DatiAddizionaliPrenotante_2___testo',
        #                                  [appointment_data['amount_minor_kids']])
        pass

    def complete_visa_appointment_data(self, appointment_data):
        # FIXME: Need to add multiple appointment support
        # Fill passport expiry date input. Format needs to be "yyyy-mm-dd"
        find_element_by_id_and_send_keys(self.driver, 'DatiAddizionaliPrenotante_0___data',
                                         [appointment_data['passport_expiry_date']])

        # Fill travel reason input
        travel_reason = Select(self.driver.find_element(By.ID, 'ddls_1'))
        travel_reason.select_by_visible_text(
            sanitize_appointment_reason(appointment_data['travel_reason'].capitalize()))

    def complete_id_card_data(self, appointment_data):
        # FIXME: Need to add multiple appointment support
        # Fill address input
        find_element_by_id_and_send_keys(self.driver, 'DatiAddizionaliPrenotante_0___testo',
                                         [appointment_data['address']])

        have_kids_select = Select(self.driver.find_element(By.ID, 'ddls_1'))
        time.sleep(0.1)
        have_kids_select.select_by_visible_text(appointment_data['have_kids'].capitalize())

        # Fill minor kids amount input
        find_element_by_id_and_send_keys(self.driver, 'DatiAddizionaliPrenotante_2___testo',
                                         [appointment_data['amount_minor_kids']])

        # Fill height input
        find_element_by_id_and_send_keys(self.driver, 'DatiAddizionaliPrenotante_3___testo',
                                         [appointment_data['height']])

        # Fill zip code input
        find_element_by_id_and_send_keys(self.driver, 'DatiAddizionaliPrenotante_4___testo',
                                         [appointment_data['zip_code']])

        # Fill other citizenship input
        find_element_by_id_and_send_keys(self.driver, 'DatiAddizionaliPrenotante_5___testo',
                                         [appointment_data['other_citizenships'].capitalize()])

        # Fill marital status input
        marital_status_input = Select(self.driver.find_element(By.ID, 'ddls_6'))
        marital_status_input.select_by_visible_text(return_full_marital_status(appointment_data['marital_status']))

    def complete_appointment_details(self, appointment_data):
        appointment_data = appointment_data['appointment_type'].upper()
        if appointment_data['appointment_type'] == 'PASAPORTE':
            self.complete_passport_appointment_data(appointment_data)
        if appointment_data['appointment_type'] == 'CIUDADANIA PADRES':
            self.complete_family_citizenship_data(appointment_data)
        if appointment_data['appointment_type'] == 'VISADOS':
            self.complete_visa_appointment_data(appointment_data)
        if appointment_data['appointment_type'] == 'CARTA DE IDENTIDAD':
            self.complete_id_card_data(appointment_data)
        # There's no need for completing any data for descendent citizenship appointment

    def raise_exception_on_non_available_appointment_warning_presence(self):
        try:
            wait_presence_of_element_located_by_xpath(self.driver, 1,
                                                      './/div[text()="Al momento non ci sono date disponibili per il servizio richiesto"]')
            raise Exception('Non available appointments warning detected')
        except NoSuchElementException:
            pass
