from tqdm import tqdm
import os
from seleniumbase import Driver
from geneanetItemToMd import GeneanetItemToMd
from individu import Individu
import utils
from datetime import datetime
from tqdm import tqdm
import re


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
        self.individus = []

    def _start_browser(self):
        print("Start browser...")
        self.driver = Driver(browser="firefox",
                             headless=False, locale_code='fr')

    def quit(self):
        self.driver.quit()

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

    def searchFamilyName(self, name, first_name=""):
        css_family_name = 'div.row:nth-child(5) > div:nth-child(1) > input:nth-child(1)'
        family_name_field = self.driver.find_element(css_family_name)
        family_name_field.send_keys(name)

        if (first_name != ""):
            css_first_name = "div.row:nth-child(5) > div:nth-child(2) > input:nth-child(1)"
            first_name_field = self.driver.find_element(css_first_name)
            first_name_field.send_keys(first_name)

        css_search_button = "button.button"
        search_button = self.driver.find_element(css_search_button)
        search_button.click()

        css_archive_toggle = "#categories_1-archives"
        self.driver.wait_for_element_visible(
            css_archive_toggle, timeout=20)
        self.loopOnPagesSearch()

    def loopOnPagesSearch(self):
        totalPageNbr = self.getCurrentTotalPageNbr()
        maxNbrItemInPage = 70
        for i in tqdm(range(totalPageNbr), desc="Page Loop"):
            for j in tqdm(range(maxNbrItemInPage), desc="Item Loop", leave=False):
                self.handle_item(j)
            self.clickOnNextPage()

        self.merge_individus()

        self.process_individus()
        print("end processing search.")

    def process_individus(self):
        for individu in tqdm(self.individus):
            last_name = individu.get_last_name()
            first_name = individu.get_first_name()
            date_naissance = individu.get_birth_date()

            try:
                date_naissance = utils.parse_date(date_naissance)
            except ValueError:
                date_naissance = None

            folder_individu = utils.to_upper_camel_case(
                last_name + ' ' + first_name)
            if date_naissance is not None:
                folder_individu += f" - {date_naissance.year}"

            folder_individu_path = os.path.join(
                self.individu_folder, folder_individu)

            # Check if folder exists, and if so, add a suffix
            i = 1
            original_folder_individu_path = folder_individu_path
            while os.path.exists(folder_individu_path):
                folder_individu_path = f"{original_folder_individu_path} - {i}"
                i += 1

            # Move src archives if necessary
            self.move_src_archive(
                individu, folder_individu_path, last_name, first_name)

            GeneanetItemToMd(individu, folder_individu_path,
                             self.file_path_to_template_individu)

    def move_src_archive(self, individu, folder_individu_path, last_name, first_name):
        src_attributes = ['death_src', 'wedding_src', 'birth_src']

        # Handle src attributes
        for src_attr in src_attributes:
            src = getattr(individu, src_attr)
            if src and "TOMOVE(" in src:
                self.process_tomove(src, src_attr, individu,
                                    folder_individu_path, last_name, first_name)

        # Handle other_informations
        for index, info in enumerate(individu.other_informations):
            if "TOMOVE(" in info:
                self.process_tomove(info, 'other_informations', individu,
                                    folder_individu_path, last_name, first_name, index=index)

    def process_tomove(self, src, src_attr, individu, folder_individu_path, last_name, first_name, index=None):
        # Extract the path inside the parentheses
        path_to_move = re.search(r"TOMOVE\((.*?)\)", src).group(1)
        # Move the file to the individual's folder
        moved_file_path = utils.move_file_to_folder(
            folder_individu_path, path_to_move)

        if moved_file_path:

            # Determine the type of archive
            if src_attr == 'birth_src':
                type_archive = "Naissance"
                new_filename = f"Archive {type_archive}"
            elif src_attr == 'death_src':
                type_archive = "Deces"
                new_filename = f"Archive {type_archive}"
            elif src_attr == 'wedding_src':
                type_archive = "Mariage"
                new_filename = f"Archive {type_archive}"
            else:
                new_filename = "Presse"
                type_archive = "Autre"

            # Extract the file extension
            file_extension = os.path.splitext(moved_file_path)[1]

            # New filename
            new_filename += f" {last_name} {first_name}{file_extension}"
            new_filename = utils.to_upper_camel_case(new_filename)

            # Rename the file
            renamed_file_path = utils.rename_file(
                folder_individu_path, os.path.basename(moved_file_path), new_filename)

            if renamed_file_path:
                # Update the src attribute in individu
                new_src = src.replace(
                    f"TOMOVE({path_to_move})", f"![]({new_filename})")
                if src_attr == 'other_informations' and index is not None:
                    individu.other_informations[index] = new_src
                else:
                    setattr(individu, src_attr, new_src)

    def merge_individus(self):
        merged_individus = []
        visited = set()

        for i, individu in tqdm(enumerate(self.individus)):
            if i in visited:
                continue

            # Check for duplicates
            duplicates = [individu]

            for j, other_individu in enumerate(self.individus[i + 1:], start=i + 1):
                if j in visited:
                    continue

                if (individu.last_name == other_individu.last_name and
                        individu.first_name == other_individu.first_name):
                    if (individu.birth_date and other_individu.birth_date and
                            individu.birth_date == other_individu.birth_date) or \
                            (individu.death_date and other_individu.death_date and
                             individu.death_date == other_individu.death_date) or \
                            (individu.wedding_date and other_individu.wedding_date and
                             individu.wedding_date == other_individu.wedding_date):
                        duplicates.append(other_individu)
                        visited.add(j)

            # Merge duplicates
            merged_individu = self.merge_duplicates(duplicates)
            merged_individus.append(merged_individu)
            visited.add(i)

        self.individus = merged_individus

    def merge_duplicates(self, duplicates):
        merged = duplicates[0]
        for individu in duplicates[1:]:
            if not merged.sexe and individu.sexe:
                merged.set_sex(individu.sexe)
            if not merged.profession and individu.profession:
                merged.set_profession(individu.profession)
            if not merged.civil_state_notes and individu.civil_state_notes:
                merged.set_civil_state_notes(individu.civil_state_notes)
            if not merged.civil_state_src and individu.civil_state_src:
                merged.set_civil_state_src(individu.civil_state_src)
            if not merged.birth_date and individu.birth_date:
                merged.set_birth_date(individu.birth_date)
            if not merged.birth_place and individu.birth_place:
                merged.set_birth_place(individu.birth_place)
            if not merged.father and individu.father:
                merged.set_father(individu.father)
            if not merged.mother and individu.mother:
                merged.set_mother(individu.mother)
            if not merged.birth_notes and individu.birth_notes:
                merged.set_birth_notes(individu.birth_notes)
            if not merged.birth_src and individu.birth_src:
                merged.set_birth_src(individu.birth_src)
            if not merged.death_date and individu.death_date:
                merged.set_death_date(individu.death_date)
            if not merged.death_place and individu.death_place:
                merged.set_death_place(individu.death_place)
            if not merged.death_notes and individu.death_notes:
                merged.set_death_notes(individu.death_notes)
            if not merged.death_src and individu.death_src:
                merged.set_death_src(individu.death_src)
            if not merged.partner and individu.partner:
                merged.set_partner(individu.partner)
            if not merged.wedding_date and individu.wedding_date:
                merged.set_wedding_date(individu.wedding_date)
            if not merged.wedding_place and individu.wedding_place:
                merged.set_wedding_place(individu.wedding_place)
            if not merged.wedding_notes and individu.wedding_notes:
                merged.set_wedding_notes(individu.wedding_notes)
            if not merged.wedding_src and individu.wedding_src:
                merged.set_wedding_src(individu.wedding_src)
            merged.other_informations.extend(individu.other_informations)

        return merged

    def handle_item(self, j):
        css_line_j = f"a.ligne-resultat:nth-child({j})"
        if self.driver.is_element_present(css_line_j):
            type_line, sub_type = self.retrieve_type_line(css_line_j)
            if (type_line == ""):
                return
            last_name, first_name = self.getNameLine(css_line_j)
            last_name = utils.sanitize_path_component(last_name)
            first_name = utils.sanitize_path_component(first_name)
            places = self.getPlaceLine(css_line_j)
            dates = self.get_associated_date(css_line_j)

            # Create an Individu object and set its properties
            individu_j = Individu(last_name, first_name)
            if (type_line == "Archive"):
                self.handle_archive_line(
                    css_line_j, sub_type, last_name, first_name, places, dates, individu_j)
            elif (type_line == "Presse"):
                self.handle_presse_line(
                    css_line_j, sub_type, last_name, first_name, places, dates, individu_j)

            for place_pair in places:
                place, type_place = place_pair
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

            self.individus.append(individu_j)

    def handle_archive_line(self, css_line_j, type_archive, last_name, first_name, places, dates, individu_j):
        content_acte, src_acte, src_archive = self.get_associated_archive(
            css_line_j, last_name, first_name, type_archive)
        if (type_archive == "Décès"):
            if (src_archive != ""):
                individu_j.set_death_src(
                    f"TOMOVE({src_archive})")
            else:
                if (content_acte != ""):
                    individu_j.set_death_notes(
                        content_acte)
                if (src_acte != ""):
                    individu_j.set_death_src(
                        src_acte)
        elif (type_archive == "Mariage"):
            if (src_archive != ""):
                individu_j.set_wedding_src(
                    f"TOMOVE({src_archive})")
            else:
                if (content_acte != ""):
                    individu_j.set_wedding_notes(
                        content_acte)
                if (src_acte != ""):
                    individu_j.set_wedding_src(
                        src_acte)
        elif (type_archive == "Naissance"):
            if (src_archive != ""):
                individu_j.set_birth_src(
                    f"TOMOVE({src_archive})")
            else:
                if (content_acte != ""):
                    individu_j.set_birth_notes(
                        content_acte)
                if (src_acte != ""):
                    individu_j.set_birth_src(
                        src_acte)
        elif ("Autres" in type_archive):
            content_autre = f"# {type_archive}\n\n"
            if (len(places) > 0):
                type_place, place = places[0]
                content_autre += f"- __Lieu évenement__ :{place}\n"

            if (len(dates) > 0):
                type_date, date = places[0]
                content_autre += f"- __Date évenement__ :{date}\n"
            individu_j.add_other(content_autre)

    def handle_presse_line(self, css_line_j, type_presse, last_name, first_name, places, dates, individu_j):
        src_press, file_download_path = self.get_associated_presse(
            css_line_j, last_name, first_name)

        content_autre = f"# {type_presse}\n\n"
        if (len(places) > 0):
            type_place, place = places[0]
            content_autre += f"- __Lieu évenement__ :{place}\n"

        if (len(dates) > 0):
            type_date, date = places[0]
            content_autre += f"- __Date évenement__ :{date}\n"

        if (file_download_path != ""):
            content_autre += f"TOMOVE({file_download_path})\n"
        if (src_press != ""):
            content_autre += f"- __Source__ : {src_press}\n"

        individu_j.add_other(content_autre)

    def get_associated_presse(self, css_line_j, last_name, first_name):
        css_type_press = css_line_j + \
            " > div:nth-child(1) > div:nth-child(1) > img:nth-child(1)"
        is_image = self.driver.is_element_visible(css_type_press)
        src_press = ""
        file_download_path = ""
        if (is_image):
            link_to_new_page = self.driver.get_attribute(
                css_line_j, "href")
            self.driver.switch_to.new_window(link_to_new_page)
            self.driver.open(link_to_new_page)
            # It automatically download when open the page
            # css_download = "#download"
            # time_check = 0
            # time_out = 20
            # time_wait_between_2_check = 0.1
            # while (self.driver.is_element_visible(css_download) is False):
            #     time_check += time_wait_between_2_check
            #     self.driver.sleep(time_wait_between_2_check)
            #     if (time_check > time_out):
            #         print(
            #             "\nUnable to found download button "
            #             f" text for {last_name} {first_name} with css : {css_line_j}.")
            #         "Unknown windows, we close it.\n"
            #         break

            # if (self.driver.is_element_visible(css_download)):
            # self.driver.click(css_download)
            has_complete_download, file_download = utils.wait_for_download(
                self.download_path, 20)
            if (has_complete_download):
                file_download_path = os.path.join(
                    self.download_path, file_download)
            # print("close")
            self.driver.close()
            self.driver.switch_to.window(
                self.driver.window_handles[0])
        else:
            css_button_popup = ".button-container > a:nth-child(1)"
            self.driver.click(css_line_j)
            if (self.driver.is_element_visible(css_button_popup)):
                link_to_new_page = self.driver.get_attribute(
                    css_button_popup, "href")
                self.driver.switch_to.new_window(link_to_new_page)
                self.driver.open(link_to_new_page)

                css_new_page = "body"
                time_check = 0
                time_out = 20
                time_wait_between_2_check = 0.1
                while (self.driver.is_element_visible(css_new_page) is False):
                    time_check += time_wait_between_2_check
                    self.driver.sleep(time_wait_between_2_check)
                    if (time_check > time_out):
                        print(
                            "\nUnable to load page "
                            f" text for {last_name} {first_name} with css : {css_line_j}.")
                        "Unknown windows, we close it.\n"
                        break
                if (self.driver.is_element_visible(css_new_page)):
                    src_press = self.driver.current_url

                self.driver.close()
                self.driver.switch_to.window(
                    self.driver.window_handles[0])

        return (src_press, file_download_path)

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
            print("\nUnable to find date\n")
            return []

    def get_associated_archive(self, css_line_j, last_name, first_name, type_archive):
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
        file_download_path = ""
        while (self.driver.is_element_visible(css_download) is False) and (self.driver.is_element_visible(css_releve_collab) is False):
            time_check += time_wait_between_2_check
            self.driver.sleep(time_wait_between_2_check)
            if (time_check > time_out):
                print(
                    "\nUnable to found download button or releve collaboratif"
                    f" text for {last_name} {first_name} with css : {css_line_j}.")
                "Unknown windows, we close it.\n"
                break

        if (self.driver.is_element_visible(css_download)):
            self.driver.click(css_download)
            has_complete_download, file_download = utils.wait_for_download(
                self.download_path, 20)
            if (has_complete_download):
                file_download_path = os.path.join(
                    self.download_path, file_download)
        if (self.driver.is_element_visible(css_releve_collab)):
            css_content_acte = ".acte-content"
            css_src_acte = ".releve-detail-container > div:nth-child(2)"
            # there are 2 types of pages here
            # css_src_acte_2 = "#expertsys-sources-modal-openlink"
            css_src_acte_2 = "tr.not-printable"
            if self.driver.is_element_present(css_content_acte):
                content_acte = self.driver.get_text(css_content_acte)
                content_acte = "\n" + \
                    utils.format_string_to_bullets(content_acte)
            else:
                print("\nUnable to get the content of the acte of "
                      f"{last_name} {first_name} with css : {css_line_j}.\n")
            if self.driver.is_element_present(css_src_acte):
                src_acte = self.driver.get_text(css_src_acte)
                src_acte = "\n" + utils.format_string_to_bullets(src_acte)
                css_src_access = "#expertsys-sources-modal-link"
                if (self.driver.is_element_present(css_src_access)):
                    self.driver.click(css_src_access)
                    src_acte = self.find_src_in_archive(
                        src_acte, last_name, first_name, css_line_j)
                else:
                    print(f"\nUnable to get any further source of the acte of "
                          f"{last_name} {first_name} with css : {css_line_j}."
                          f"\nWe found didn't find this css {css_src_access}")
            else:
                if (self.driver.is_element_present(css_src_acte_2)):
                    css_src_access = "#expertsys-sources-modal-openlink"
                    self.driver.click(css_src_access)
                    src_acte = self.find_src_in_archive(
                        src_acte, last_name, first_name, css_line_j)
                else:
                    print(f"\nUnable to get any the source of the acte of "
                          f"{last_name} {first_name} with css : {css_line_j}."
                          f"\nWe found neither this css"
                          f"{css_src_acte} nor this css {css_src_acte_2}")

        self.driver.close()
        self.driver.switch_to.window(
            self.driver.window_handles[0])
        return (content_acte, src_acte, file_download_path)

    def find_src_in_archive(self, src_acte, last_name, first_name, css_line_j):
        css_list_src = ".expertsys-bullet"
        try:
            self.driver.wait_for_element_visible(
                css_list_src, timeout=3)
        except:
            print(f"\nUnable to open the research original "
                  f"act pop up for {last_name} {first_name}"
                  f"with css : {css_line_j}\n")
            return src_acte
        src_acte += f"\n\t- Lien registres : "
        index_src = 1
        css_list_k_src = f".expertsys-bullet >" + \
            f" li:nth-child({index_src}) > a:nth-child(1)"
        while self.driver.is_element_present(css_list_k_src):
            link_src_k = self.driver.get_attribute(css_list_k_src, "href")
            src_acte += f"[Registre {index_src}]({link_src_k}) ou "
            index_src += 1
            css_list_k_src = f".expertsys-bullet > " +\
                f"li:nth-child({index_src}) > a:nth-child(1)"
        return src_acte

    def retrieve_type_line(self, css_line):
        css_line_info = css_line + " > div:nth-child(2) > div:nth-child(1)"
        typeLine = ""
        if self.driver.is_element_present(css_line_info):
            typeLine = self.driver.get_text(css_line_info)

        if ("Archives : " in typeLine):
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
            return ("Archive", typeArchive)
        elif ("Presse : " in typeLine):
            return ("Presse", typeLine)
        return ("", "")

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
        if (self.driver.is_element_visible(css_total_page_nbr)):
            self.total_page_nbr = int(self.driver.get_text(css_total_page_nbr))
        else:
            self.total_page_nbr = 1
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

        css_close_pop_up = "a.close-reveal-modal:nth-child(3)"
        if (self.driver.is_element_visible(css_close_pop_up)):
            close_button = self.driver.find_element(css_close_pop_up)
            close_button.click()

        next_page_button = self.driver.find_element(css_click_on_next_page)

        next_page_button.click()
        self.current_page_nbr += 1

        css_archive_toggle = "#categories_1-archives"
        self.driver.wait_for_element_visible(
            css_archive_toggle, timeout=20)
