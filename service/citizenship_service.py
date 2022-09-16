import datetime
import time

from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By

from config.config import settings as config_file
from helpers.logger import logger
from helpers.retry_function import retry_on_exception
from helpers.save_html_content_to_file import save_html_content_to_file
from helpers.webdriver.find_element import find_element_by_id_and_send_keys, \
    find_element_by_xpath_and_click_it_with_javascript, find_element_by_id_and_click_it_with_javascript
from helpers.webdriver.waits import wait_presence_of_element_located_by_id, wait_presence_of_element_located_by_xpath
from webdrivers.webdriver import WebDriver


def sleep_if_necessary():
    current_time = datetime.datetime.today()
    if current_time.hour == 23:
        if current_time.minute >= 50:
            future = datetime.datetime(current_time.year, current_time.month, current_time.day, 0, 0, 0)
            future += datetime.timedelta(days=1)
            logger.info('Sleeping for {} seconds'.format((future - current_time).total_seconds()))
            time.sleep((future - current_time).total_seconds())


class CitizenshipService:
    def __init__(self, unlimited_wait):
        self.driver = None
        self.config = config_file.crawling
        self.unlimited_wait = unlimited_wait

    def schedule_citizenship_appointment(self, login_credentials, appointment_data):
        response = False
        try:
            # FIXME: We're using here general appointment_configs instead of citizenship_appointment_configs
            logger.info('Creating browser')
            self.driver = WebDriver().acquire(self.config.citizenship_controller.webdriver_type)
            self.driver.maximize_window()
            self.driver.get('https://prenotami.esteri.it/')
            self.log_in_user(login_credentials)

            # Waiting for user area page to be fully loaded
            wait_presence_of_element_located_by_id(self.driver, 5, 'advanced', self.unlimited_wait,
                                                   'Timeout waiting after login in user')

            self.search_for_available_appointment(appointment_data)

            logger.info('Should be an available appointment. Start searching')
            self.select_available_appointment_or_raise_exception()

            # Accept appointment
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            find_element_by_xpath_and_click_it_with_javascript(self.driver, './/button[contains(text(), "Reservar")]')
            response = True

            # Wait until visibility of 'print' button
            wait_presence_of_element_located_by_id(self.driver, 5, 'btnStampa')

            # TODO: We need to save this to send it to the client
            self.driver.save_full_page_screenshot()

        except Exception as ex:
            logger.exception(ex)
        finally:
            self.driver.close()
            self.driver.quit()
            logger.info('Webdriver fully destroyed')

            return response

    @retry_on_exception(5, retry_sleep_time=5)
    def log_in_user(self, client_login_data):
        # Waiting for login page to be fully loaded
        wait_presence_of_element_located_by_id(self.driver, 5, 'login-email', self.unlimited_wait,
                                               'Unable to locate email input text')
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # Complete username field
        logger.info('Logging user {}'.format(client_login_data['username']))
        find_element_by_id_and_send_keys(self.driver, 'login-email', [client_login_data['username']])

        # Complete password field
        find_element_by_id_and_send_keys(self.driver, 'login-password', [client_login_data['password'], Keys.ENTER])

    @retry_on_exception(max_attempts=100, retry_sleep_time=5)
    def search_for_available_appointment(self, appointment_data):
        logger.info('Selecting appointment type descendant citizenship')
        self.driver.get('https://prenotami.esteri.it/Services/Booking/340')
        self.raise_exception_on_non_available_appointment_warning_presence()

        wait_presence_of_element_located_by_id(self.driver, 5, 'PrivacyCheck', self.unlimited_wait,
                                               'Timeout waiting for privacyCheck box to be present')


        # Saving html information in case anything fails we'll have a backup
        filename = 'citizenship_service_form#{}'.format(datetime.datetime.now().strftime("%Y-%m-%d"))
        save_html_content_to_file(self.driver.page_source, filename, 'html', '/tmp/prenotami-esteri/htmls')

        # FIXME: Unfinished work here. Empty function body
        self.complete_citizenship_appointment_data(appointment_data)

        # Click privacy checkbox
        find_element_by_id_and_click_it_with_javascript(self.driver, 'PrivacyCheck')

        # Click next button
        find_element_by_id_and_click_it_with_javascript(self.driver, 'btnAvanti')

        self.driver.switch_to.alert.accept()

        logger.info('Data completition finished. Checking for available appointments')
        self.check_calendar_or_raise_exception()

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

    def select_available_appointment_or_raise_exception(self):
        loop = 0
        while True:
            if loop > 25:
                raise Exception('No appointments for next two years')
            try:
                if loop == 0:
                    # Saving html information in case anything fails we'll have a backup
                    filename = 'citizenship_service_calendar#{}'.format(datetime.datetime.now().strftime("%Y-%m-%d"))
                    save_html_content_to_file(self.driver.page_source, filename, 'html', '/tmp/prenotami-esteri/htmls')

                wait_presence_of_element_located_by_xpath(self.driver, 3, './/td[@class="day availableDay"]')
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
                    wait_presence_of_element_located_by_xpath(self.driver, 5, './/span[@title="Next Month"]')
                    # Click next month button
                    find_element_by_xpath_and_click_it_with_javascript(self.driver, './/span[@title="Next Month"]')
                    loop += 1
                except NoSuchElementException:
                    raise Exception('Unable to pick appointment')
                except TimeoutException:
                    raise Exception('Timeout waiting for click NextMonth button')

    def complete_citizenship_appointment_data(self, appointment_data):
        pass

    def raise_exception_on_non_available_appointment_warning_presence(self):
        try:
            wait_presence_of_element_located_by_xpath(self.driver, 10,
                                                      './/div[text()="Al momento non ci sono date disponibili per il servizio richiesto"]')
            raise Exception('Non available appointments warning detected')
        except NoSuchElementException:
            pass
