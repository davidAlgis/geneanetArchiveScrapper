import argparse
import datetime
from geneanetItemToMd import GeneanetItemToMd
from geneanetScrapper import GeneanetScrapper

parser = argparse.ArgumentParser(
    description='Generate markdown files from genealogy data.')
parser.add_argument('-d', '--directory', type=str, default='Individus',
                    help='the directory where the markdown files will be generated (default: Individus)')
parser.add_argument('-t', '--template', type=str, default='template.md',
                    help='the path to the template file for the markdown files (default: template.md)')
args = parser.parse_args()

# Usage
scraper = GeneanetScrapper(args.directory)
# login = input("Please enter your login to geneanet :")
# password = getpass.getpass("Please enter your password for geneanet : ")
scraper.connect("david.algis@tutamail.com", "mdpTest67")
scraper.searchFamilyName("Algis")
