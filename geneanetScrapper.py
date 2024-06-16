import os
import getpass
from seleniumbase import Driver


class GeneanetScraper:
    def __init__(self, headless=True):
        self.path, filename = os.path.split(os.path.realpath(__file__))
        self.headless = headless
        self.driver = None
        self.is_connected = False

    def _start_browser(self):
        print("Start browser...")
        chrome_driver_path = os.path.join(
            self.path, "driver", "chromedriver.exe")
        self.driver = Driver(browser="firefox",
                             uc=True, headless=False)

    def find_button_and_click(driver, xpath):
        """
        This function finds a button using the given XPATH and clicks it.
        It returns True if the button was found and clicked, and False otherwise.
        """
        try:
            button = driver.find_element(By.XPATH, xpath)
            button.click()
            return True
        except NoSuchElementException:
            return False

    def find_field_and_fill(driver, xpath, value):
        """
        This function finds a field using the given XPATH and fills it with the given value.
        It returns True if the field was found and filled, and False otherwise.
        """
        try:
            field = driver.find_element(By.XPATH, xpath)
            field.send_keys(value)
            return True
        except NoSuchElementException:
            return False

    def connect(self, id, password):
        self._start_browser()

        self.driver.get(
            "https://www.geneanet.org/connexion/")

        # Wait for the page to load
        xpath_id_field = '#_username'
        # xpath_pwd_field = '/html/body/div[1]/div/div[5]/div/div/div[1]/div[1]/div[1]/form/div[1]/input'
        xpath_pwd_field = '#_password'
        # xpath_connect_button = '/html/body/div[1]/div/div[5]/div/div/div[1]/div[1]/div[1]/form/div[2]/div[2]/button'
        xpath_connect_button = '//*[@id="_submit"]'
        xpath_deny_cookie_button = '/html/body/div[2]/div[3]/button[2]'
        self.driver.wait_for_element_visible(
            xpath_id_field, by="xpath", timeout=20)
        self.driver.wait_for_element_visible(
            xpath_deny_cookie_button, by="xpath", timeout=20)

        deny_cookie_button = self.driver.find_element(
            xpath_deny_cookie_button)
        # for a unknown reason we need to click 3 times
        # to makes the button accept the request
        deny_cookie_button.click()
        deny_cookie_button.click()
        deny_cookie_button.click()

        # Enter the id
        id_field = self.driver.find_element(xpath_id_field)
        id_field.send_keys(id)

        # Enter the password
        pwd_field = self.driver.find_element(xpath_pwd_field)
        pwd_field.send_keys(password)

        # Click the connect button
        connect_button = self.driver.find_element(
            xpath_connect_button)
        connect_button.click()

        # Wait for the page to load
        xpath_show_my_tree = '/html/body/div[1]/div/div[5]/div/div/div[1]/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div[2]/div/a[1]'
        WebDriverWait(self.driver, 20).until(
            EC.visibility_of_element_located((By.XPATH, xpath_show_my_tree)))

        self.is_connected = True


# Usage

scraper = GeneanetScraper()
login = input("Please enter your login to geneanet :")
password = getpass.getpass("Please enter your password for geneanet : ")
scraper.connect(login, password)
