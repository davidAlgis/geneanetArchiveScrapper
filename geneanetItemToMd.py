import os
import re
import utils
from datetime import datetime
import chardet


class GeneanetItemToMd:
    def __init__(self, individu, path_to_md, file_path_to_template):
        self.individu = individu
        self.path_to_md = path_to_md
        self.file_path_to_template = file_path_to_template

        self.setup_file()
        self.fill_all_fields()

    def setup_file(self):
        file_individu = utils.to_upper_camel_case(
            self.individu.last_name + ' ' + self.individu.first_name)
        try:
            date_naissance = utils.parse_date(self.individu.birth_date)
        except ValueError:
            date_naissance = None
        if date_naissance:
            self.filename = f"{file_individu} - {date_naissance.year}.md"
        else:
            self.filename = f"{file_individu}.md"
        path_to_md = utils.sanitize_path(self.path_to_md)

        self.filepath = os.path.join(path_to_md, self.filename)

        # check if output directory exists, and if not, create it
        if not os.path.isdir(path_to_md):
            os.makedirs(path_to_md)

        # check if file exists, and if not, create it and copy the template into it
        if not os.path.isfile(self.filepath):
            with open(self.file_path_to_template, "r") as template_file:
                template_content = template_file.read()

            with open(self.filepath, "w", encoding='utf-8') as f:
                f.write(template_content.format(
                    last_name=self.individu.last_name, first_name=self.individu.first_name))

    def fill_all_fields(self):
        self.fill_field("Nom", self.individu.last_name)
        self.fill_field("Prenom", self.individu.first_name)
        self.fill_field("Sexe", self.individu.sexe)
        self.fill_field("Profession", self.individu.profession)
        self.fill_field("Notes etat civil", self.individu.civil_state_notes)
        self.fill_field("Sources etat civil", self.individu.civil_state_src)
        self.fill_field("Date de naissance",
                        self.format_date(self.individu.birth_date))
        self.fill_field("Lieu de naissance", self.individu.birth_place)
        self.fill_field("Pere", self.individu.father)
        self.fill_field("Mere", self.individu.mother)
        self.fill_field("Notes naissance", self.individu.birth_notes)
        self.fill_field("Sources naissance", self.individu.birth_src)
        self.fill_field("Date de deces", self.format_date(
            self.individu.death_date))
        self.fill_field("Lieu du deces", self.individu.death_place)
        self.fill_field("Notes deces", self.individu.death_notes)
        self.fill_field("Sources deces", self.individu.death_src)
        self.fill_field("Conjoint", self.individu.partner)
        self.fill_field("Date de mariage", self.format_date(
            self.individu.wedding_date))
        self.fill_field("Lieu du mariage", self.individu.wedding_place)
        self.fill_field("Notes mariage", self.individu.wedding_notes)
        self.fill_field("Sources mariage", self.individu.wedding_src)
        for info in self.individu.other_informations:
            self.add_other(info)

    def format_date(self, date):
        try:
            date_to_write = utils.parse_date(date)
            if date_to_write:
                date_to_write = utils.date_to_string(date_to_write)
            else:
                date_to_write = date
        except ValueError:
            date_to_write = date
        return date_to_write

    def fill_field(self, fieldName, fieldContent):
        if fieldContent is None:
            fieldContent = "Inconnu"

        # Determine the encoding of the file
        with open(self.filepath, "rb") as f:
            raw_data = f.read()
            result = chardet.detect(raw_data)
        encoding = result["encoding"]

        try:
            # Read the content with detected encoding
            content = raw_data.decode(encoding)
        except (UnicodeDecodeError, TypeError):
            # Fall back to UTF-8 if detected encoding fails
            content = raw_data.decode('utf-8', errors='ignore')

        # Find the existing content for the field, if any
        existing_content = re.findall(f"__{fieldName}__ :.*\n", content)
        if not existing_content:
            print(f"Field __{fieldName}__ not found in file {self.filepath}")
            return

        existing_content = existing_content[0]

        # Replace the existing content with the new content
        content = content.replace(
            existing_content, f"__{fieldName}__ : {fieldContent}\n")

        # Ensure no extra lines are added by using consistent line endings
        content = content.replace("\r\n", "\n").replace("\n\n", "\n")

        # Write the content back using UTF-8 encoding
        with open(self.filepath, "w", encoding="utf-8") as f:
            f.write(content)
    def add_other(self, data):
        data = "\n" + data + "\n"
        with open(self.filepath, "a", encoding="utf-8") as f:
            f.write(data)
