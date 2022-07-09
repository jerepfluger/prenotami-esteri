from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


def wait_presence_of_element_located_by_id(driver, timeout, descriptor_property, unlimited_wait=False, message=''):
    if unlimited_wait:
        _unlimited_wait_presence_of_element_located_by_id(driver, descriptor_property)
    else:
        wait_presence_of_element_located(driver, timeout, By.ID, descriptor_property, message)


def wait_presence_of_element_located_by_xpath(driver, timeout, descriptor_property, unlimited_wait=False, message=''):
    if unlimited_wait:
        _unlimited_wait_presence_of_element_located_by_xpath(driver, descriptor_property)
    else:
        wait_presence_of_element_located(driver, timeout, By.XPATH, descriptor_property, message)


def wait_presence_of_element_located(driver, timeout, descriptor_type, descriptor_property, message=''):
    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((descriptor_type, descriptor_property)), message)


def _unlimited_wait_presence_of_element_located_by_id(driver, id_property_name):
    unlimited_wait_presence_of_element_located(driver, By.ID, id_property_name)


def _unlimited_wait_presence_of_element_located_by_xpath(driver, descriptor_property):
    unlimited_wait_presence_of_element_located(driver, By.XPATH, descriptor_property)


def unlimited_wait_presence_of_element_located(driver, descriptor_type, descriptor_property):
    while True:
        try:
            WebDriverWait(driver, 5, poll_frequency=1).until(
                EC.presence_of_element_located((descriptor_type, descriptor_property)))
            break
        except TimeoutException:
            pass
