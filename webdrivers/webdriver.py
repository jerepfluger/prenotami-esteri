from selenium import webdriver
from selenium.webdriver import ChromeOptions, FirefoxOptions

from config.config import settings
from helpers.logger import logger


class ChromeWebdriver:
    @staticmethod
    def create(proxy=None):
        logger.info("Creating Chromium Web Driver")
        options = ChromeOptions()
        options.binary_location = settings.web_driver.chrome_binary
        options.add_argument('headless')
        options.add_argument('hide-scrollbars')
        options.add_argument('disable-gpu')
        options.add_argument('no-sandbox')
        options.add_argument('data-path={}'.format(settings.web_driver.chromium.data_path))
        options.add_argument('disk-cache-dir={}'.format(settings.web_driver.chromium.cache_dir))
        options.add_argument('disable-infobars')
        # Disable web security for get ember components via execute-scripts
        options.add_argument('disable-web-security')
        if proxy:
            options.add_argument('proxy-server={}:{}'.format(proxy.host, proxy.port))

        return webdriver.Chrome(chrome_options=options)


class FirefoxWebdriver:
    @staticmethod
    def create(proxy=None):
        proxy = proxy
        logger.info("Creating Firefox Web Driver")

        options = FirefoxOptions()
        options.binary_location = settings.web_driver.firefox_binary
        # options.add_argument('--headless')
        options.add_argument('--new_instance')

        #  https://developer.mozilla.org/en-US/docs/Mozilla/Preferences/Mozilla_networking_preferences
        options.set_preference('browser.cache.disk.enable', 'true')
        options.set_preference('browser.cache.memory.enable', 'true')
        options.set_preference('browser.cache.disk.parent_directory', settings.web_driver.firefox.cache_dir)
        # https://github.com/mozilla/geckodriver/issues/517#issuecomment-286701282
        options.set_preference("browser.tabs.remote.autostart", "false")
        options.set_preference("browser.tabs.remote.autostart.1", "false")
        options.set_preference("browser.tabs.remote.autostart.2", "false")
        options.set_preference("browser.tabs.remote.force-enable", "false")
        # more settings
        options.set_preference("dom.ipc.processCount", "1")
        options.set_preference("browser.sessionstore.interval", "50000000")
        options.set_preference("browser.sessionstore.max_resumed_crashes", "0")
        options.set_preference("browser.sessionstore.max_tabs_undo", "0")
        options.set_preference("browser.sessionstore.max_windows_undo", "0")
        options.set_preference("dom.popup_maximum", 0)
        options.set_preference("privacy.popups.showBrowserMessage", False)
        options.set_preference("privacy.popups.disable_from_plugins", 3)
        # Proxy
        if proxy:
            logger.info("Setting proxy values to http {} and port {}".format(proxy.host, proxy.port))
            firefox_capabilities = webdriver.DesiredCapabilities.FIREFOX
            firefox_proxy = "{}:{}".format(proxy.host, proxy.port)
            firefox_capabilities['proxy'] = {
                "proxyType": "MANUAL",
                "httpProxy": firefox_proxy,
                "ftpProxy": firefox_proxy,
                "sslProxy": firefox_proxy
            }

            return webdriver.Firefox(options=options, log_path="/dev/null",
                                     capabilities=firefox_capabilities)

        return webdriver.Firefox(options=options, log_path="/dev/null",
                                 service_log_path="/dev/null")


class WebDriver:
    def __init__(self):
        self.web_driver_creators = {'firefox': FirefoxWebdriver.create, 'chromium': ChromeWebdriver.create}

    def acquire(self, webdriver_type, proxy=None):
        if webdriver_type in self.web_driver_creators:
            return self.web_driver_creators[webdriver_type](proxy)

        return None
