import os
import re
import utils
from datetime import datetime
import chardet


class GeneanetItemToMd:
    def __init__(self, last_name, first_name, path_to_md, file_path_to_template):
        self.initialize_fields()
        self.last_name = last_name
        self.first_name = first_name

        self.setup_file(path_to_md, file_path_to_template)

        self.fill_field("Nom", self.last_name)
        self.fill_field("Prenom", self.first_name)

    @classmethod
    def with_birth_date(cls, last_name, first_name, birth_date, path_to_md, file_path_to_template):
        instance = cls.__new__(cls)
        instance.initialize_fields()
        instance.last_name = last_name
        instance.first_name = first_name
        instance.birth_date = birth_date

        instance.setup_file(path_to_md, file_path_to_template, birth_date)

        instance.fill_field("Nom", instance.last_name)
        instance.fill_field("Prenom", instance.first_name)
        instance.fill_field("Date de naissance", birth_date)

        return instance

    def initialize_fields(self):
        # Civil state
        self.sexe = "Inconnu"
        self.profession = "Inconnu"
        self.civil_state_notes = ""
        self.civil_state_src = "Inconnu"

        # Birth
        self.birth_date = None
        self.birth_place = "Inconnu"
        self.father = "Inconnu"
        self.mother = "Inconnu"
        self.birth_notes = ""
        self.birth_src = "Inconnu"

        # Death
        self.death_date = None
        self.death_place = "Inconnu"
        self.death_notes = ""
        self.death_src = "Inconnu"

        # Wedding
        self.partner = "Inconnu"
        self.wedding_date = None
        self.wedding_place = "Inconnu"
        self.wedding_notes = ""
        self.wedding_src = "Inconnu"
        self.other_informations = []

    def setup_file(self, path_to_md, file_path_to_template, birth_date=None):
        file_individu = utils.to_upper_camel_case(
            self.last_name + ' ' + self.first_name)
        if birth_date:
            self.filename = f"{file_individu} - {birth_date.year}.md"
        else:
            self.filename = f"{file_individu}.md"
        path_to_md = utils.sanitize_path(path_to_md)

        self.filepath = os.path.join(path_to_md, self.filename)

        # check if output directory exists, and if not, create it
        if not os.path.isdir(path_to_md):
            os.makedirs(path_to_md)

        # check if file exists, and if not, create it and copy the template into it
        if not os.path.isfile(self.filepath):
            with open(file_path_to_template, "r") as template_file:
                template_content = template_file.read()

            with open(self.filepath, "w") as f:
                f.write(template_content.format(
                    last_name=self.last_name, first_name=self.first_name))

    def fill_field(self, fieldName, fieldContent):
        # Determine the encoding of the file
        with open(self.filepath, "rb") as f:
            result = chardet.detect(f.read())
        encoding = result["encoding"]

        try:
            # Read the content with detected encoding
            with open(self.filepath, "r", encoding=encoding) as f:
                content = f.read()
        except (UnicodeDecodeError, TypeError):
            # Fall back to UTF-8 if detected encoding fails
            with open(self.filepath, "r", encoding="utf-8") as f:
                content = f.read()

        # Find the existing content for the field, if any
        existing_content = re.findall(f"__{fieldName}__ :.*\n", content)
        if not existing_content:
            print(f"Field __{fieldName}__ not found in file {self.filepath}")
            return

        existing_content = existing_content[0]

        # Replace the existing content with the new content
        content = content.replace(
            existing_content, f"__{fieldName}__ : {fieldContent}\n")

        with open(self.filepath, "w", encoding="utf-8") as f:
            f.write(content)

    def add_other(self, data):
        data = "\n" + data + "\n"
        self.other_informations.append(data)
        with open(self.filepath, "a") as f:
            f.write(data)

    def set_sex(self, sexe):
        self.sexe = sexe
        self.fill_field("Sexe", self.sexe)

    def set_profession(self, profession):
        self.profession = profession
        self.fill_field("Profession", self.profession)

    def set_civil_state_notes(self, notes):
        self.civil_state_notes = notes
        self.fill_field("Notes etat civil", self.civil_state_notes)

    def set_civil_state_src(self, src):
        self.civil_state_src = src
        self.fill_field("Sources etat civil", self.civil_state_src)

    def set_birth_date(self, date):
        try:
            date_to_write = utils.parse_date(date)
            if date_to_write:
                date_to_write = utils.date_to_string(date_to_write)
            else:
                date_to_write = date
        except ValueError:
            date_to_write = date
        self.birth_date = date_to_write
        self.fill_field("Date de naissance", date_to_write)

    def set_birth_place(self, place):
        self.birth_place = place
        self.fill_field("Lieu de naissance", place)

    def set_father(self, father):
        self.father = father
        self.fill_field("Pere", father)

    def set_mother(self, mother):
        self.mother = mother
        self.fill_field("Mere", mother)

    def set_birth_notes(self, notes):
        self.birth_notes = notes
        self.fill_field("Notes naissance", notes)

    def set_birth_src(self, src):
        self.birth_src = src
        self.fill_field("Sources naissance", src)

    def set_death_date(self, date):
        try:
            date_to_write = utils.parse_date(date)
            if date_to_write:
                date_to_write = utils.date_to_string(date_to_write)
            else:
                date_to_write = date
        except ValueError:
            date_to_write = date
        self.death_date = date
        self.fill_field("Date de deces", date_to_write)

    def set_death_place(self, place):
        self.death_place = place
        self.fill_field("Lieu du deces", place)

    def set_death_notes(self, notes):
        self.death_notes = notes
        self.fill_field("Notes deces", notes)

    def set_death_src(self, src):
        self.death_src = src
        self.fill_field("Sources deces", src)

    def set_partner(self, partner):
        self.partner = partner
        self.fill_field("Conjoint", partner)

    def set_wedding_date(self, date):
        try:
            if date_to_write:
                date_to_write = utils.date_to_string(date_to_write)
            else:
                date_to_write = date
        except ValueError:
            date_to_write = date

        self.wedding_date = date
        self.fill_field("Date de mariage", date_to_write)

    def set_wedding_place(self, place):
        self.wedding_place = place
        self.fill_field("Lieu du mariage", place)

    def set_wedding_notes(self, notes):
        self.wedding_notes = notes
        self.fill_field("Notes mariage", notes)

    def set_wedding_src(self, src):
        self.wedding_src = src
        self.fill_field("Sources mariage", src)
