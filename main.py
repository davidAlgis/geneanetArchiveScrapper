import argparse
import datetime
from geneanetItemToMd import GeneanetItemToMd
from geneanetScrapper import GeneanetScrapper

parser = argparse.ArgumentParser(description='Generate markdown files from genealogy data.')
parser.add_argument('-d', '--directory', type=str, default='Individus',
                    help='the directory where the markdown files will be generated (default: Individus)')
parser.add_argument('-t', '--template', type=str, default='template.md',
                    help='the path to the template file for the markdown files (default: template.md)')
args = parser.parse_args()

# Usage
# scraper = GeneanetScrapper()
# login = input("Please enter your login to geneanet :")
# password = getpass.getpass("Please enter your password for geneanet : ")
# scraper.connect("david.algis@tutamail.com", "mdpTest67")
# scraper.searchFamilyName("Algis")import argparse

# create a new instance of the GeneanetItemToMd class with the command-line arguments
item = GeneanetItemToMd("Dupont", "Jean", path_to_md=args.directory, file_path_to_template=args.template)

# Set civil state fields
item.set_sex("Masculin")
item.set_profession("Charpentier")
item.set_civil_state_notes("Notes sur l'état civil de Jean Dupont")
item.set_civil_state_src("Source de l'état civil de Jean Dupont")

# Set birth fields
item.set_birth_date(datetime.date(1980, 5, 17))
item.set_birth_place("Paris")
item.set_father("Pierre Dupont")
item.set_mother("Marie Durand")
item.set_birth_notes("Notes sur la naissance de Jean Dupont")
item.set_birth_src("Source de la naissance de Jean Dupont")

# Set death fields
item.set_death_date(datetime.date(2050, 2, 3))
item.set_death_place("Lyon")
item.set_death_notes("Notes sur le décès de Jean Dupont")
item.set_death_src("Source du décès de Jean Dupont")

# Set wedding fields
item.set_partner("Laura Martin")
item.set_wedding_date(datetime.date(2010, 9, 12))
item.set_wedding_place("Marseille")
item.set_wedding_notes("Notes sur le mariage de Jean Dupont et Laura Martin")
item.set_wedding_src("Source du mariage de Jean Dupont et Laura Martin")
