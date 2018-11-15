#!/usr/bin/env python3.6
# -*- coding: utf8 -*-

'''
ELQuent.menu
Authentication and main menu for ELQuent

Mateusz Dąbrowski
github.com/MateuszDabrowski
linkedin.com/in/mateusz-dabrowski-marketing/
'''

# Python imports
import os
import re
import sys
import json
import shutil
import pickle
import requests
from colorama import Fore, init

# ELQuent imports
import utils.mail as mail
import utils.link as link
import utils.page as page
import utils.cert as cert
import utils.campaign as campaign
import utils.webinar as webinar
import utils.database as database
import utils.export as export
import utils.validator as validator
import utils.modifier as modifier
import utils.admin as admin
import utils.api.api as api

# Initialize colorama
init(autoreset=True)


'''
=================================================================================
                            File Path Getter
=================================================================================
'''


def file(file_path):
    '''
    Returns file path to template files
    '''

    def find_data_file(filename, directory='main'):
        '''
        Returns correct file path for both script and frozen app
        '''
        if directory == 'main':  # Files in main directory
            if getattr(sys, 'frozen', False):
                datadir = os.path.dirname(sys.executable)
            else:
                datadir = os.path.dirname(os.path.dirname(__file__))
            return os.path.join(datadir, filename)
        elif directory == 'api':  # Auths saved in api directory
            if getattr(sys, 'frozen', False):
                datadir = os.path.dirname(sys.executable)
            else:
                datadir = os.path.dirname(os.path.dirname(__file__))
            return os.path.join(datadir, 'utils', directory, filename)

    file_paths = {
        'incomes': find_data_file('incomes'),
        'outcomes': find_data_file('outcomes'),
        'utils': find_data_file('utils.json'),
        'readme': find_data_file('readme.md'),
        'country': find_data_file('country.p', directory='api'),
        'eloqua': find_data_file('eloqua.p', directory='api'),
        'naming': find_data_file('naming.json', directory='api')
    }

    return file_paths.get(file_path)


# Builds folders for user
os.makedirs(file('incomes'), exist_ok=True)
os.makedirs(file('outcomes'), exist_ok=True)


'''
=================================================================================
                            Source Country Getter
=================================================================================
'''


def get_source_country():
    '''
    Returns source country either from the user input or shelve
    » source_country: two char str
    '''
    if not os.path.isfile(file('country')):
        print(f'\n{Fore.WHITE}What is your Source Country?')
        source_country_list = COUNTRY_UTILS['country']
        for i, country in enumerate(source_country_list):
            print(
                f'{Fore.WHITE}[{Fore.YELLOW}{i}{Fore.WHITE}]\t{Fore.GREEN}WK{Fore.WHITE}{country}')

        while True:
            print(f'{Fore.WHITE}Enter number associated with you country: ', end='')
            try:
                choice = int(input(' '))
            except ValueError:
                print(f'{Fore.RED}Please enter numeric value!')
                continue
            if 0 <= choice < len(source_country_list):
                break
            else:
                print(f'{Fore.RED}Entered value does not belong to any country!')
        source_country = source_country_list[choice]
        pickle.dump(source_country, open(file('country'), 'wb'))
    source_country = pickle.load(open(file('country'), 'rb'))

    return source_country


'''
=================================================================================
                        Checks if updates are available
=================================================================================
'''


def new_version():
    '''
    Returns True if there is newer version of the app available
    '''
    # Gets current version number of running app
    with open(file('readme'), 'r', encoding='utf-8') as files:
        readme = files.read()
    check_current_version = re.compile(r'\[_Version: (.*?)_\]', re.UNICODE)
    current_version = check_current_version.findall(readme)

    # Gets available version number on Github
    github = requests.get('https://github.com/MateuszDabrowski/ELQuent')
    check_available_version = re.compile(
        r'\[<em>Version: (.*?)</em>\]', re.UNICODE)
    available_version = check_available_version.findall(github.text)

    current_main_version = ('').join(current_version[0].split('.')[:2])
    available_main_version = ('').join(available_version[0].split('.')[:2])
    if current_main_version < available_main_version:
        print(
            f'{Fore.WHITE}[{Fore.RED}ERROR{Fore.WHITE}] {Fore.YELLOW}Update ELQuent to newer version')
        input('')
        raise SystemExit

    # Compares versions
    return bool(current_version != available_version)


'''
=================================================================================
                            Cleaner helper functions
=================================================================================
'''


def clean_outcomes():
    '''
    Cleans all content of Outcomes folder
    '''
    for files in os.listdir(file('outcomes')):
        file_path = os.path.join(file('outcomes'), files)
        if os.path.isfile(file_path):
            os.unlink(file_path)
        else:
            shutil.rmtree(file_path, ignore_errors=False, onerror=None)
    print(f'\n{Fore.GREEN}» Outcomes folder cleaned.')

    return


def clean_incomes():
    '''
    Cleans all content of Incomes folder
    '''
    for files in os.listdir(file('incomes')):
        file_path = os.path.join(file('incomes'), files)
        if os.path.isfile(file_path):
            os.unlink(file_path)
        else:
            shutil.rmtree(file_path, ignore_errors=False, onerror=None)
    print(f'\n{Fore.GREEN}» Incomes folder cleaned.')

    return


def clean_folders(_):
    '''
    Cleaning functions menu
    '''
    print(
        f'\n{Fore.GREEN}ELQuent.clean Utilites:'
        f'\n{Fore.WHITE}[{Fore.YELLOW}1{Fore.WHITE}]\t»',
        f'{Fore.WHITE}[{Fore.YELLOW}Incomes{Fore.WHITE}] Clean Incomes folder'
        f'\n{Fore.WHITE}[{Fore.YELLOW}2{Fore.WHITE}]\t»',
        f'{Fore.WHITE}[{Fore.YELLOW}Outcomes{Fore.WHITE}] Clean Outcomes folder'
        f'\n{Fore.WHITE}[{Fore.YELLOW}3{Fore.WHITE}]\t»',
        f'{Fore.WHITE}{Fore.WHITE}[{Fore.YELLOW}Both{Fore.WHITE}] Clean Incomes & Outcomes folders'
        f'\n{Fore.WHITE}[{Fore.YELLOW}Q{Fore.WHITE}]\t»',
        f'{Fore.WHITE}[{Fore.YELLOW}Quit to main menu{Fore.WHITE}]'
    )
    while True:
        print(f'{Fore.YELLOW}Enter number associated with chosen utility:', end='')
        choice = input(' ')
        if choice.lower() == 'q':
            break
        elif choice == '1':
            clean_incomes()
            break
        elif choice == '2':
            clean_outcomes()
            break
        elif choice == '3':
            clean_incomes()
            clean_outcomes()
            break
        else:
            print(f'{Fore.RED}Entered value does not belong to any utility!')
            choice = ''


'''
=================================================================================
                                    Main menu
=================================================================================
'''


def menu(choice=''):
    '''
    Allows to choose ELQuent utility
    '''
    print(f'\n{Fore.GREEN}-----------------------------------------------------------------------------')

    # Loads json file with naming convention
    with open(file('naming'), 'r', encoding='utf-8') as naming_file:
        naming = json.load(naming_file)

    # Builds matrix with available utils
    utils = {
        'clean_folders': (clean_folders, f'Folder{Fore.WHITE}] Clean files in Income/Outcome folders'),
        'change_links': (link.link_module, f'Link{Fore.WHITE}] Change utm_track and elqTrack codes in e-mail links'),
        'build_mail': (mail.mail_constructor, f'Mail{Fore.WHITE}] Build e-mail from package in Incomes folder'),
        'page_gen': (page.page_gen, f'Page{Fore.WHITE}] Swap or Add Form to a single Landing Page'),
        'campaign_gen': (campaign.campaign_module, f'Campaign{Fore.WHITE}] Build various Eloqua campaigns'),
        'contacts': (database.contact_list, f'Contacts{Fore.WHITE}] Create contact upload file with correct structure'),
        'validator': (validator.validator_module, f'Validator{Fore.WHITE}] Test and validate assets and campaigns'),
        'modifier': (modifier.modifier_module, f'Modifier{Fore.WHITE}] Modify multiple assets at once'),
        'webinar': (webinar.click_to_elq, f'Webinar{Fore.WHITE}] Upload Webinar registered users and attendees'),
        'cert': (cert.cert_constructor, f'Certificate{Fore.WHITE}] Create certificates and upload with contacts'),
        'export': (export.export_module, f'Export{Fore.WHITE}] Export and save campaign or activity data'),
        'mail_groups': (admin.admin_module, f'Admin{Fore.WHITE}] WKCORP flows')
    }

    # Access to all utils for admin
    if ELOQUA_USER.lower() == 'mateusz.dabrowski':
        available_utils = utils
    # Gets dict of utils available for users source country
    else:
        utils_list = COUNTRY_UTILS[SOURCE_COUNTRY]
        if ELOQUA_USER.lower() in naming[SOURCE_COUNTRY]['advanced_users']:
            utils_list.extend(COUNTRY_UTILS['ADVANCED'])
        available_utils = {k: v for (k, v) in utils.items() if k in utils_list}
    util_names = list(available_utils.keys())

    # Lists utils available to chosen user
    print(f'\n{Fore.GREEN}ELQuent Utilites:')
    for i, function in enumerate(available_utils.values()):
        print(
            f'{Fore.WHITE}[{Fore.YELLOW}{i}{Fore.WHITE}]\t» [{Fore.YELLOW}{function[1]}')
    print(
        f'{Fore.WHITE}[{Fore.YELLOW}Q{Fore.WHITE}]\t» [{Fore.YELLOW}Quit{Fore.WHITE}]')

    # Asks user to choose utility
    while True:
        if not choice:
            print(
                f'{Fore.YELLOW}Enter number associated with chosen utility:', end='')
            choice = input(' ')
        if choice.lower() == 'q':
            print(f'\n{Fore.GREEN}Ahoj!')
            raise SystemExit
        try:
            choice = int(choice)
        except (TypeError, ValueError):
            print(f'{Fore.RED}Please enter numeric value!')
            choice = ''
            continue
        if 0 <= choice < len(available_utils):
            break
        else:
            print(f'{Fore.RED}Entered value does not belong to any utility!')
            choice = ''

    print(f'\n{Fore.GREEN}-----------------------------------------------------------------------------')

    available_utils.get(util_names[choice])[0](SOURCE_COUNTRY)


'''
=================================================================================
                                Main program flow
=================================================================================
'''


print(f'\n{Fore.GREEN}Ahoj!')

# Checks if there is newer version of the app
if new_version():
    print(
        f'\n{Fore.WHITE}[{Fore.RED}!{Fore.WHITE}]{Fore.RED} Newer version available')

# Loads utils.json containing source countries and utils available for them
with open(file('utils'), 'r', encoding='utf-8') as f:
    COUNTRY_UTILS = json.load(f)

# Gets required auth data and prints them
SOURCE_COUNTRY = get_source_country()

# Get eloqua auth for multiple calls
eloqua_key = api.get_eloqua_auth(SOURCE_COUNTRY)

# Load domain and user name
ELOQUA_DOMAIN, ELOQUA_USER = pickle.load(open(file('eloqua'), 'rb'))

print(
    f'\n{Fore.YELLOW}User » {Fore.WHITE}[{Fore.GREEN}{ELOQUA_DOMAIN} {SOURCE_COUNTRY}{Fore.WHITE}] {ELOQUA_USER}')

# Checks for terminal arguments of shell function
if len(sys.argv) < 2:
    menu()
elif sys.argv[1] == 'link':
    link.link_module(SOURCE_COUNTRY)
elif sys.argv[1] == 'mail':
    mail.mail_constructor(SOURCE_COUNTRY)
elif sys.argv[1] == 'page':
    page.page_gen(SOURCE_COUNTRY)
elif sys.argv[1] == 'campaign':
    campaign.campaign_module(SOURCE_COUNTRY)
elif sys.argv[1] == 'web':
    webinar.click_to_elq(SOURCE_COUNTRY)
elif sys.argv[1] == 'base':
    database.contact_list(SOURCE_COUNTRY)
elif sys.argv[1] == 'export':
    export.export_module(SOURCE_COUNTRY)
elif sys.argv[1] == 'validate':
    validator.validator_module(SOURCE_COUNTRY)
elif sys.argv[1] == 'modify':
    modifier.modifier_module(SOURCE_COUNTRY)
elif sys.argv[1] == 'password':
    print(f'{Fore.YELLOW}Key » {Fore.WHITE}{eloqua_key}')

# Allows to cycle through options after first errand
while True:
    menu()
