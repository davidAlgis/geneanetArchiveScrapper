import os
from seleniumbase import Driver
from geneanetItemToMd import GeneanetItemToMd
import utils


class GeneanetScrapper():
    def __init__(self, individu_folder, file_path_to_template_individu, headless=True):
        self.path, filename = os.path.split(os.path.realpath(__file__))
        self.headless = headless
        self.driver = None
        self.is_connected = False
        self.total_page_nbr = 1
        self.current_page_nbr = 1
        self.download_path = ".\\downloaded_files"
        self.file_path_to_template_individu = file_path_to_template_individu
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

    def loopOnPagesSearch(self):
        totalPageNbr = self.getCurrentTotalPageNbr()
        # Add tqdm to this loop
        maxNbrItemInPage = 100
        for i in range(totalPageNbr):
            for j in range(maxNbrItemInPage):
                self.handle_item(j)
            return
            self.clickOnNextPage()

    def handle_item(self, j):
        css_line_j = f"a.ligne-resultat:nth-child({j})"
        if self.driver.is_element_present(css_line_j):
            isArchive, typeArchive = self.isArchiveLine(css_line_j)
            if (isArchive):
                last_name, first_name = self.getNameLine(css_line_j)
                places = self.getPlaceLine(css_line_j)
                dates = self.get_associated_date(css_line_j)

                folder_individu = utils.to_upper_camel_case(
                    last_name + ' ' + first_name)
                folder_individu_path = os.path.join(
                    self.individu_folder, folder_individu)
                content_acte, src_acte, src_archive = self.get_associated_archive(
                    css_line_j, last_name, first_name, folder_individu_path, typeArchive)
                print(src_archive)
                name_image = ""
                if (len(src_archive.split('\\')) > 0):
                    name_image = src_archive.split('\\')[-1]
                individu_j = GeneanetItemToMd(last_name, first_name,
                                              folder_individu_path, self.file_path_to_template_individu)
                if (typeArchive == "Décès"):
                    if (src_archive != ""):
                        individu_j.set_death_src(
                            f"cf. ![]({name_image})")
                    else:
                        if (content_acte != ""):
                            individu_j.set_death_notes(
                                content_acte)
                        if (src_acte != ""):
                            individu_j.set_death_src(
                                src_acte)
                elif (typeArchive == "Mariage"):
                    if (src_archive != ""):
                        individu_j.set_wedding_src(
                            f"cf. ![]({name_image})")
                    else:
                        if (content_acte != ""):
                            individu_j.set_wedding_notes(
                                content_acte)
                        if (src_acte != ""):
                            individu_j.set_wedding_src(
                                src_acte)
                elif (typeArchive == "Naissance"):
                    if (src_archive != ""):
                        individu_j.set_birth_src(
                            f"cf. ![]({name_image})")
                    else:
                        if (content_acte != ""):
                            individu_j.set_birth_notes(
                                content_acte)
                        if (src_acte != ""):
                            individu_j.set_birth_src(
                                src_acte)
                elif ("Autres" in typeArchive):
                    content_autre = f"# {typeArchive}\n\n"
                    if (len(places) > 0):
                        type_place, place = places[0]
                        content_autre += f"- __Lieu évenement__ :{place}\n"

                    if (len(dates) > 0):
                        type_date, date = places[0]
                        content_autre += f"- __Date évenement__ :{date}\n"
                    individu_j.add_other(content_autre)

                for place_pair in places:
                    type_place, place = place_pair
                    if (type_place == "Décès"):
                        individu_j.set_death_place(place)
                    elif (type_place == "Mariage"):
                        individu_j.set_wedding_place(place)
                    elif (type_place == "Naissance"):
                        individu_j.set_birth_place(place)
                for date_pair in dates:
                    type_date, date = date_pair
                    if (type_date == "Décès"):
                        individu_j.set_death_date(date)
                    elif (type_date == "Mariage"):
                        individu_j.set_wedding_date(date)
                    elif (type_date == "Naissance"):
                        individu_j.set_birth_date(date)

    def get_associated_date(self, css_line):
        css_date = css_line + " > div:nth-child(2) > div:nth-child(2)"
        if (self.driver.is_element_visible(css_date)):
            date = self.driver.get_text(css_date)
            # Split the string into lines
            lines = date.strip().split('\n')

            # Initialize an empty list to hold the pairs
            pairs = []

            # Iterate over each line
            for line in lines:
                # Split the line into parts
                parts = line.split()

                # If there are exactly two parts, add them as a pair to the list
                if len(parts) == 2:
                    pairs.append((parts[0], parts[1]))
            return pairs
        else:
            print("Unable to find date")
            return []

    def get_associated_archive(self, css_line_j, last_name, first_name, folder_individu_path, type_archive):
        link_to_new_page = self.driver.get_attribute(
            css_line_j, "href")
        self.driver.switch_to.new_window(link_to_new_page)
        self.driver.open(link_to_new_page)

        css_download = "button.svg-icon-viewer-download"
        css_releve_collab = "#content-wrapper > h1:nth-child(2)"
        time_check = 0
        time_out = 20
        time_wait_between_2_check = 0.1
        content_acte = ""
        src_acte = ""
        src_archive = ""
        while (self.driver.is_element_visible(css_download) is False) and (self.driver.is_element_visible(css_releve_collab) is False):
            time_check += time_wait_between_2_check
            self.driver.sleep(time_wait_between_2_check)
            if (time_check > time_out):
                print(
                    "Unable to found download button or releve collaboratif"
                    "text. Unknown windows, we close it")

        if (self.driver.is_element_visible(css_download)):
            self.driver.click(css_download)
            has_complete_download, file_download = utils.wait_for_download(
                self.download_path, 20)
            if (has_complete_download):
                file_download_path = os.path.join(
                    self.download_path, file_download)
                utils.move_file_to_folder(
                    folder_individu_path, file_download_path)
                file_extension = os.path.splitext(file_download)[1]
                if ("Autre" in type_archive):
                    type_archive = "Autre"
                new_file_name = "Archive" + ' ' + type_archive + ' ' + \
                    last_name + ' ' + first_name + ' ' + file_extension
                new_file_name = utils.to_upper_camel_case(new_file_name)
                new_file_name = utils.rename_file(
                    folder_individu_path, file_download, new_file_name)
                src_archive = new_file_name
        if (self.driver.is_element_visible(css_releve_collab)):
            css_content_acte = ".acte-content"
            css_src_acte = ".releve-detail-container > div: nth-child(2)"
            if self.driver.is_element_present(css_content_acte):
                content_acte = self.driver.get_text(css_content_acte)
            else:
                print("Unable to get the content of the acte")
            if self.driver.is_element_present(css_src_acte):
                src_acte = self.driver.get_text(css_src_acte)
            else:
                print("Unable to get the source of the acte")

        self.driver.close()
        self.driver.switch_to.window(
            self.driver.window_handles[0])
        return (content_acte, src_acte, src_archive)

    def isArchiveLine(self, css_line):
        css_line_info = css_line + " > div:nth-child(2) > div:nth-child(1)"
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
                text_archive = typeLine.replace('\n', ' ')
                typeArchive = f"Autres - {text_archive}"
            return (True, typeArchive)
        return (False, "")

    def getNameLine(self, css_line):
        css_line_info = css_line + " > div:nth-child(2) > div:nth-child(1)"

        infoLine = self.driver.get_text(css_line_info)
        infoLine_split = infoLine.split('\n')
        if (len(infoLine_split) > 0):
            return utils.split_name(infoLine_split[0])

        return ("", "")

    def getPlaceLine(self, css_line):
        k = 1
        css_line_place_k = css_line + \
            f"> div:nth-child(2) > div:nth-child(3) > p:nth-child({k})"
        pairs = []
        while self.driver.is_element_present(css_line_place_k):
            css_line_place = css_line_place_k + \
                " > span:nth-child(2)"
            place = self.driver.get_text(css_line_place)
            css_line_type_place = css_line_place_k + \
                " > span:nth-child(1) > span:nth-child(1)"

            icon_class_name = self.driver.get_attribute(
                css_line_type_place, "class")
            if ("grave" in icon_class_name):
                pairs.append((place, "Décès"))
            elif ("Union" in icon_class_name):
                pairs.append((place, "Mariage"))
            elif ("Birth" in icon_class_name):
                pairs.append((place, "Naissance"))
            elif ("House" in icon_class_name):
                pairs.append((place, "Autres"))
            else:
                pairs.append((place, "Inconnu"))
            k += 1
            css_line_place_k = css_line + \
                f"> div:nth-child(2) > div:nth-child(3) > p:nth-child({k})"
        return pairs

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
