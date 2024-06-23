import os
from seleniumbase import Driver
from geneanetItemToMd import GeneanetItemToMd
import utils


class GeneanetScrapper():
    def __init__(self, individu_folder, headless=True):
        self.path, filename = os.path.split(os.path.realpath(__file__))
        self.headless = headless
        self.driver = None
        self.is_connected = False
        self.total_page_nbr = 1
        self.current_page_nbr = 1
        self.download_path = ".\\downloaded_files"
        self.individu_folder = individu_folder

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
                self.handle_item(j)

                # self.driver.sleep(3)
                # self.driver.close()
                # self.driver.switch_to.window(
                #     self.driver.window_handles[0])

                # itemGeneanetJ = GeneanetItemToMd(last_name, first_name)
                # return

            self.clickOnNextPage()

    def handle_item(self, j):
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

                has_complete_download, file_download = utils.wait_for_download(
                    self.download_path, 20)
                if (has_complete_download):
                    folder_individu = utils.to_upper_camel_case(
                        last_name + ' ' + first_name)
                    folder_individu_path = os.path.join(
                        self.individu_folder, folder_individu)
                    file_download_path = os.path.join(
                        self.download_path, file_download)
                    utils.move_file_to_folder(
                        folder_individu_path, file_download_path)
                    file_extension = os.path.splitext(file_download)[1]
                    new_file_name = "Archive" + ' ' + typeArchive + ' ' \
                        + last_name + ' ' + first_name + ' ' + file_extension
                    new_file_name = utils.to_upper_camel_case(new_file_name)
                    new_file_name = utils.rename_file(
                        folder_individu_path, file_download, new_file_name)
                    # new_file_path = os.path.join(
                    # self.download_path, new_file_name)

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
            return utils.split_name(infoLine_split[0])

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
