import os
import getpass
import time
from seleniumbase import Driver
from geneanetItemToMd import GeneanetItemToMd

def split_name(name):
    # Split the string into a list of words
    words = name.split()
    # The last name is the first word, and the first name is the second word
    last_name = words[0]
    first_names = ' '.join(words[1:])
    # Return the last name and first name as a tuple
    return (last_name, first_names)


def to_upper_camel_case(string):
    # Split the string into words
    words = string.split()
    # Capitalize the first letter of each word and join them together
    camel_case_string = ''.join(word.capitalize() for word in words)
    return camel_case_string


def wait_for_download(directory, max_wait_time=10, sleep_time=0.2):
    start_time = time.time()
    while True:
        files_in_directory = os.listdir(directory)
        if files_in_directory:
            try:
                latest_file = max(files_in_directory, key=lambda f: os.path.getctime(
                    os.path.join(directory, f)))
                if not os.path.isfile(os.path.join(directory, latest_file)):
                    continue
                else:
                    print(f"Download complete. File: {latest_file}")
                    return True, latest_file
            except FileNotFoundError:
                print("File not found. Skipping...")
                continue

        if time.time() - start_time > max_wait_time:
            print("Max wait time reached. Download not completed.")
            return False, None

        time.sleep(sleep_time)


def rename_file(directory, current_filename, new_filename):
    current_file_path = os.path.join(directory, current_filename)
    new_file_path = os.path.join(directory, new_filename)
    counter = 1

    while os.path.exists(new_file_path):
        new_file_path_without_ext = os.path.splitext(new_file_path)[0]
        new_file_ext = os.path.splitext(new_file_path)[1]
        new_file_path = f"{new_file_path_without_ext}_{counter}{new_file_ext}"
        counter += 1

    try:
        os.rename(current_file_path, new_file_path)
    except FileNotFoundError:
        print(f"File {current_filename} not found.")
    except Exception as e:
        print(f"Error renaming file: {str(e)}")


class GeneanetScrapper():
    def __init__(self, headless=True):
        self.path, filename = os.path.split(os.path.realpath(__file__))
        self.headless = headless
        self.driver = None
        self.is_connected = False
        self.total_page_nbr = 1
        self.current_page_nbr = 1
        self.download_path = ".\\downloaded_files"

    def _start_browser(self):
        print("Start browser...")
        self.driver = Driver(browser="firefox",
                             headless=False, locale_code='fr')

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
        self.loopOnPagesSearch()
        # archive_toggle = self.driver.find_element(css_archive_toggle)
        # archive_toggle.click()

        # css_civil_state = "div.checked:nth-child(1) > div:nth-child(2) > label:nth-child(1)"
        # self.driver.wait_for_element_visible(
        #     css_civil_state, timeout=20)

    def loopOnPagesSearch(self):
        totalPageNbr = self.getCurrentTotalPageNbr()
        # Add tqdm to this loop
        maxNbrItemInPage = 100
        for i in range(totalPageNbr):
            for j in range(maxNbrItemInPage):
                css_line_j = f"a.ligne-resultat:nth-child({j})"
                if self.driver.is_element_present(css_line_j):
                    isArchive, typeArchive = self.isArchiveLine(css_line_j)
                    if (isArchive):
                        last_name, first_name = self.getNameLine(css_line_j)
                        place, type_place = self.getPlaceLine(css_line_j)

                        link_to_new_page = self.driver.get_attribute(
                            css_line_j, "href")
                        self.driver.switch_to.new_window(link_to_new_page)
                        self.driver.open(link_to_new_page)
                        css_download = "button.svg-icon-viewer-download"
                        self.driver.wait_for_element_visible(
                            css_download, timeout=20)
                        self.driver.click(css_download)

                        has_complete_download, file_download = wait_for_download(
                            self.download_path, 20)
                        if (has_complete_download):
                            file_extension = os.path.splitext(file_download)[1]
                            new_file_name = "Archive" + ' ' + typeArchive + ' ' \
                                + last_name + ' ' + first_name + ' ' + file_extension
                            new_file_name = to_upper_camel_case(new_file_name)
                            rename_file(
                                self.download_path, file_download, new_file_name)
                            print("rename to ", new_file_name)
                        # self.driver.sleep(3)
                        # self.driver.close()
                        # self.driver.switch_to.window(
                        #     self.driver.window_handles[0])

                        # itemGeneanetJ = GeneanetItemToMd(last_name, first_name)
                        return

            self.clickOnNextPage()

    def isArchiveLine(self, css_line):
        css_line_info = css_line + \
            " > div:nth-child(2) > div:nth-child(1)"
        typeLine = ""
        if self.driver.is_element_present(css_line_info):
            typeLine = self.driver.get_text(css_line_info)

        if ("Archive" in typeLine):
            if ("Mariage" in typeLine):
                typeArchive = "Mariage"
            elif ("Naissance" in typeLine):
                typeArchive = "Naissance"
            elif ("Décès" in typeLine):
                typeArchive = "Décès"
            elif ("Cimetière" in typeLine):
                typeArchive = "Décès"
            else:
                typeArchive = "Inconnu"
            return (True, typeArchive)
        return (False, "")

    def getNameLine(self, css_line):
        css_line_info = css_line + \
            " > div:nth-child(2) > div:nth-child(1)"

        infoLine = self.driver.get_text(css_line_info)
        infoLine_split = infoLine.split('\n')
        if (len(infoLine_split) > 0):
            print(infoLine_split[0])
            return split_name(infoLine_split[0])

        return ("", "")

    def getPlaceLine(self, css_line):
        css_line_place = css_line + \
            " > div:nth-child(2) > div:nth-child(3) > p:nth-child(1) > span:nth-child(2)"
        place = self.driver.get_text(css_line_place)
        css_line_type_place = css_line + \
            " > div:nth-child(2) > div:nth-child(3) > p:nth-child(1) > span:nth-child(1) > span:nth-child(1)"
        icon_class_name = self.driver.get_attribute(
            css_line_type_place, "class")
        if ("grave" in icon_class_name):
            return (place, "Décès")
        elif ("Union" in icon_class_name):
            return (place, "Mariage")
        elif ("Birth" in icon_class_name):
            return (place, "Naissance")
        elif ("House" in icon_class_name):
            return (place, "Autres")
        else:
            return (place, "Inconnu")

    def getCurrentTotalPageNbr(self):
        # TODO it might not work with a low page number...
        # maybe reduce the number li:nth-child(7) until it found some thing
        css_total_page_nbr = ".pagination > li:nth-child(7) > a:nth-child(1)"
        self.total_page_nbr = int(self.driver.get_text(css_total_page_nbr))
        return self.total_page_nbr

    def clickOnNextPage(self):
        if (self.current_page_nbr == 1):
            css_click_on_next_page = f".pagination > li:nth-child(3) > a:nth-child(1)"
        elif (self.current_page_nbr == 2):
            css_click_on_next_page = f".pagination > li:nth-child(5) > a:nth-child(1)"
        elif (self.current_page_nbr == 3):
            css_click_on_next_page = f".pagination > li:nth-child(6) > a:nth-child(1)"
        elif (self.current_page_nbr == self.total_page_nbr - 1):
            css_click_on_next_page = ".pagination > li:nth-child(8) > a:nth-child(1)"
        else:
            css_click_on_next_page = ".pagination > li:nth-child(7) > a:nth-child(1)"

        next_page_button = self.driver.find_element(css_click_on_next_page)
        next_page_button.click()
        self.current_page_nbr += 1

        css_archive_toggle = "#categories_1-archives"
        self.driver.wait_for_element_visible(
            css_archive_toggle, timeout=20)
