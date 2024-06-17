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
        self.driver = Driver(browser="firefox",
                             uc=True, headless=False, locale_code='fr')

    def connect(self, id, password):
        self._start_browser()

        self.driver.get(
            "https://www.geneanet.org/connexion/")

        # Wait for the page to load
        css_id_field = '#_username'
        css_pwd_field = '#_password'
        css_connect_button = '#_submit'
        css_deny_cookie_button = '#tarteaucitronAllDenied2'
        self.driver.wait_for_element_visible(
            css_id_field, timeout=20)
        self.driver.wait_for_element_visible(
            css_deny_cookie_button, timeout=20)

        deny_cookie_button = self.driver.find_element(
            css_deny_cookie_button)
        # for a unknown reason we need to click multiples times
        # to makes the button accept the request
        deny_cookie_button.click()
        nbrIter = 0
        while (self.driver.is_element_visible(css_deny_cookie_button)):
            deny_cookie_button.click()
            nbrIter += 1
            if (nbrIter > 20):
                print(
                    "Unable to click on deny cookie button.\nUnable to connect to geneanet abort")
                return False

        # Enter the id
        id_field = self.driver.find_element(css_id_field)
        id_field.send_keys(id)

        # Enter the password
        pwd_field = self.driver.find_element(css_pwd_field)
        pwd_field.send_keys(password)

        # Click the connect button
        connect_button = self.driver.find_element(
            css_connect_button)
        connect_button.click()

        # Wait for the page to load
        css_family_name = 'div.row:nth-child(5) > div:nth-child(1) > input:nth-child(1)'
        self.driver.wait_for_element_visible(
            css_family_name, timeout=20)
        self.is_connected = True
        print("Has success to connect to Geneanet.net")
        return True

    def searchFamilyName(self, name):
        css_family_name = 'div.row:nth-child(5) > div:nth-child(1) > input:nth-child(1)'
        family_name_field = self.driver.find_element(css_family_name)
        family_name_field.send_keys(name)

        css_search_button = "button.button"
        search_button = self.driver.find_element(css_search_button)
        search_button.click()

        css_archive_toggle = "#categories_1-archives"
        self.driver.wait_for_element_visible(
            css_archive_toggle, timeout=20)

        archive_toggle = self.driver.find_element(css_archive_toggle)
        archive_toggle.click()

        css_civil_state = "div.checked:nth-child(1) > div:nth-child(2) > label:nth-child(1)"
        self.driver.wait_for_element_visible(
            css_civil_state, timeout=20)


# Usage
scraper = GeneanetScraper()
# login = input("Please enter your login to geneanet :")
# password = getpass.getpass("Please enter your password for geneanet : ")
scraper.connect("david.algis@tutamail.com", "mdpTest67")
scraper.searchFamilyName("Algis")
