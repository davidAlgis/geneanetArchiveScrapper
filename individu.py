class Individu:
    def __init__(self, last_name, first_name):
        self.last_name = last_name
        self.first_name = first_name
        self.sexe = None
        self.profession = None
        self.civil_state_notes = None
        self.civil_state_src = None
        self.birth_date = None
        self.birth_place = None
        self.father = None
        self.mother = None
        self.birth_notes = None
        self.birth_src = None
        self.death_date = None
        self.death_place = None
        self.death_notes = None
        self.death_src = None
        self.partner = None
        self.wedding_date = None
        self.wedding_place = None
        self.wedding_notes = None
        self.wedding_src = None
        self.other_informations = []

    def set_sex(self, sexe):
        self.sexe = sexe

    def set_profession(self, profession):
        self.profession = profession

    def set_civil_state_notes(self, notes):
        self.civil_state_notes = notes

    def set_civil_state_src(self, src):
        self.civil_state_src = src

    def set_birth_date(self, date):
        self.birth_date = date

    def set_birth_place(self, place):
        self.birth_place = place

    def set_father(self, father):
        self.father = father

    def set_mother(self, mother):
        self.mother = mother

    def set_birth_notes(self, notes):
        self.birth_notes = notes

    def set_birth_src(self, src):
        self.birth_src = src

    def set_death_date(self, date):
        self.death_date = date

    def set_death_place(self, place):
        self.death_place = place

    def set_death_notes(self, notes):
        self.death_notes = notes

    def set_death_src(self, src):
        self.death_src = src

    def set_partner(self, partner):
        self.partner = partner

    def set_wedding_date(self, date):
        self.wedding_date = date

    def set_wedding_place(self, place):
        self.wedding_place = place

    def set_wedding_notes(self, notes):
        self.wedding_notes = notes

    def set_wedding_src(self, src):
        self.wedding_src = src

    def add_other(self, info):
        self.other_informations.append(info)

    # GETTER
    def get_last_name(self):
        return self.last_name

    def get_first_name(self):
        return self.first_name

    def get_sex(self):
        return self.sexe

    def get_profession(self):
        return self.profession

    def get_civil_state_notes(self):
        return self.civil_state_notes

    def get_civil_state_src(self):
        return self.civil_state_src

    def get_birth_date(self):
        return self.birth_date

    def get_birth_place(self):
        return self.birth_place

    def get_father(self):
        return self.father

    def get_mother(self):
        return self.mother

    def get_birth_notes(self):
        return self.birth_notes

    def get_birth_src(self):
        return self.birth_src

    def get_death_date(self):
        return self.death_date

    def get_death_place(self):
        return self.death_place

    def get_death_notes(self):
        return self.death_notes

    def get_death_src(self):
        return self.death_src

    def get_partner(self):
        return self.partner

    def get_wedding_date(self):
        return self.wedding_date

    def get_wedding_place(self):
        return self.wedding_place

    def get_wedding_notes(self):
        return self.wedding_notes

    def get_wedding_src(self):
        return self.wedding_src

    def get_other(self):
        return self.other_informations
