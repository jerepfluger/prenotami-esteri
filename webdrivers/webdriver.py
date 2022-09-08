from selenium import webdriver
from selenium.webdriver import ChromeOptions, FirefoxOptions

from config.config import settings
from helpers.logger import logger


class SafariWebdriver:
    @staticmethod
    def create(proxy=None):
        logger.info('Creating Safari Web Driver')
        options = webdriver.safari.options.Options()
        options.add_argument('headless')
        return webdriver.Safari()


class ChromeWebdriver:
    @staticmethod
    def create(proxy=None):
        logger.info('Creating Chromium Web Driver')
        options = ChromeOptions()
        options.binary_location = settings.web_driver.chrome_binary
        # options.add_argument('headless')
        options.add_argument('hide-scrollbars')
        options.add_argument('disable-gpu')
        options.add_argument('no-sandbox')
        options.add_argument('data-path={}'.format(settings.web_driver.chromium.data_path))
        options.add_argument('disk-cache-dir={}'.format(settings.web_driver.chromium.cache_dir))
        options.add_argument('disable-infobars')
        # Disable web security for get ember components via execute-scripts
        options.add_argument('disable-web-security')
        desired_capabilities = webdriver.DesiredCapabilities.CHROME
        # This flag is supposed to help pages to load complete on slow traffic site without breaking
        desired_capabilities['pageLoadStrategy'] = 'normal'

        if proxy:
            options.add_argument('proxy-server={}:{}'.format(proxy.host, proxy.port))

        return webdriver.Chrome(desired_capabilities=desired_capabilities, chrome_options=options)


class FirefoxWebdriver:
    @staticmethod
    def create(proxy=None):
        proxy = proxy
        logger.info('Creating Firefox Web Driver')

        options = FirefoxOptions()
        options.binary_location = settings.web_driver.firefox_binary
        # options.add_argument('--headless')
        options.add_argument('--new_instance')

        for item in settings.web_driver.firefox.options:
            options.set_preference(item, settings.web_driver.firefox.options[item])
        desired_capabilities = webdriver.DesiredCapabilities.FIREFOX
        # This flag is supposed to help pages to load complete on slow traffic site without breaking
        desired_capabilities['pageLoadStrategy'] = 'normal'

        # Proxy
        if proxy:
            logger.info('Setting proxy values to http {} and port {}'.format(proxy.host, proxy.port))
            firefox_proxy = '{}:{}'.format(proxy.host, proxy.port)
            desired_capabilities['proxy'] = {
                'proxyType': 'MANUAL',
                'httpProxy': firefox_proxy,
                'ftpProxy': firefox_proxy,
                'sslProxy': firefox_proxy
            }

        return webdriver.Firefox(options=options, log_path='/dev/null',
                                 service_log_path='/dev/null', capabilities=desired_capabilities)


class WebDriver:
    def __init__(self):
        self.web_driver_creators = {'firefox': FirefoxWebdriver.create, 'chromium': ChromeWebdriver.create, 'safari': SafariWebdriver.create}

    def acquire(self, webdriver_type, proxy=None):
        if webdriver_type in self.web_driver_creators:
            driver = self.web_driver_creators[webdriver_type](proxy)
            # driver.manage.add_cookie({
            #     "name": "_pk_id.E1e0Ge2p6l.5f67",
            #     "value": "c67d2105305eaa76.1651824477.12.1652365938.1652362483.",
            #     "path": "/",
            #     "domain": "prenotami.esteri.it"
            # })

            return driver
        return None
