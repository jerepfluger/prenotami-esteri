import datetime
import time

from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from config.config import settings as config_file
from helpers.logger import logger
from helpers.retry_function import retry_on_exception
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
    def __init__(self, unlimited_wait=False):
        self.driver = None
        self.config = config_file.crawling
        self.unlimited_wait = unlimited_wait

    def schedule_citizenship_appointment(self, login_credentials):
        response = False
        try:
            # FIXME: We're using here general appointment_configs instead of citizenship_appointment_configs
            self.driver = WebDriver().acquire(self.config.appointment_controller.webdriver_type)
            self.driver.maximize_window()
            self.driver.get('https://prenotami.esteri.it/')
            self.log_in_user(login_credentials)

            # Waiting for user area page to be fully loaded
            if self.unlimited_wait:
                self._unlimited_wait_presence_of_element_located_by_id('advanced')
            else:
                WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.ID, 'advanced')), 'Timeout waiting after login in user')
            self.search_for_available_appointment()

            logger.info('Should be an available appointment. Start searching')
            self.select_available_appointment_or_raise_exception()

            # Accept appointment
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            accept_appointment_button = self.driver.find_element(By.XPATH, './/button[contains(text(), "Reservar")]')
            self.driver.execute_script("arguments[0].click();", accept_appointment_button)
            response = True

            # Accept and close
            WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.ID, 'btnStampa')))

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
        if self.unlimited_wait:
            self._unlimited_wait_presence_of_element_located_by_id('login-email')
        else:
            WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.ID, 'login-email')))
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # Complete username field
        logger.info('Logging user {}'.format(client_login_data.username))
        username_input = self.driver.find_element(By.ID, 'login-email')
        username_input.send_keys(client_login_data.username)
        # Complete password field
        password_input = self.driver.find_element(By.ID, 'login-password')
        password_input.send_keys(client_login_data.password)
        password_input.send_keys(Keys.ENTER)

    @retry_on_exception(max_attempts=100, retry_sleep_time=5)
    def search_for_available_appointment(self):
        self.driver.get('https://prenotami.esteri.it/Language/ChangeLanguage?lang=13')
        if self.unlimited_wait:
            self._unlimited_wait_presence_of_element_located_by_id('advanced')
        else:
            WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.ID, 'advanced')), 'Timeout waiting for language being set to spanish')
        self.driver.get('https://prenotami.esteri.it/Services')

        # Waiting for prenotami tab to be fully loaded
        if self.unlimited_wait:
            self._unlimited_wait_presence_of_element_located_by_id('dataTableServices')
        else:
            WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.ID, 'dataTableServices')), 'Timeout waiting for appointment tab to be fully loaded')
        sleep_if_necessary()
        logger.info('Selecting appointment type descendant citizenship')
        self.driver.get('https://prenotami.esteri.it/Services/Booking/340')

        if self.unlimited_wait:
            self._unlimited_wait_presence_of_element_located_by_id('PrivacyCheck')
        else:
            WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.ID, 'PrivacyCheck')), 'Timeout waiting for privacyCheck box to be present')

        privacy_check_box = self.driver.find_element(By.ID, 'PrivacyCheck')
        self.driver.execute_script("arguments[0].click();", privacy_check_box)

        next_button = self.driver.find_element(By.ID, 'btnAvanti')
        self.driver.execute_script("arguments[0].click();", next_button)

        self.driver.switch_to.alert.accept()

        logger.info('Data completition finished. Checking for available appointments')
        self.check_calendar_or_raise_exception()

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

    def select_available_appointment_or_raise_exception(self):
        loop = 0
        while True:
            if loop > 25:
                raise Exception('No appointments for next two years')
            try:
                WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.XPATH, './/td[@class="day availableDay"]')))
                logger.info('Available appointment found!')
                available_date = self.driver.find_element(By.XPATH, './/td[@class="day availableDay"]')
                self.driver.execute_script("arguments[0].click();", available_date)
                try:
                    available_appointment = self.driver.find_elements(By.XPATH, './/div[@class="dot "]')
                    self.driver.execute_script("arguments[0].click();", available_appointment)
                except NoSuchElementException:
                    pass
                # FIXME: Here we should have a logic in case there's more than one appointment for a given day
                #  then we should be able to pick one of them (the first available) or step into the next availableDay
                #  selector for multiple appointments for a day is self.driver.find_elements(By.XPATH, './/div[@class="dot "]')
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

    def _unlimited_wait_presence_of_element_located_by_id(self, id_property_name):
        page_fully_loaded = False
        while True:
            try:
                page_fully_loaded = self.driver.execute_script('return document.readyState') == 'complete'
                WebDriverWait(self.driver, 5, poll_frequency=1).until(EC.presence_of_element_located((By.ID, id_property_name)))
                break
            except TimeoutException:
                if page_fully_loaded:
                    raise Exception('Document fully loaded and element still unavailable')
                pass
