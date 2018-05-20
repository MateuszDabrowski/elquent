#!/usr/bin/env python3.6
# -*- coding: utf8 -*-
#pylint: disable=unused-argument

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
import pickle
import requests
from colorama import Fore, init

# ELQuent imports
import utils.mail as mail
import utils.link as link
import utils.page as page
import utils.campaign as campaign
import utils.webinar as webinar
import utils.database as database
import utils.corp as corp
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
        'eloqua': find_data_file('eloqua.p', directory='api')
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

    # Compares versions
    return bool(current_version != available_version)


'''
=================================================================================
                            Cleaner helper functions
=================================================================================
'''


def clean_outcomes(country):
    '''
    Cleans all content of Outcomes folder
    '''
    for files in os.listdir(file('outcomes')):
        file_path = os.path.join(file('outcomes'), files)
        if os.path.isfile(file_path):
            os.unlink(file_path)
    print(f'\n{Fore.GREEN}» Outcomes folder cleaned.')

    return


def clean_incomes(country):
    '''
    Cleans all content of Incomes folder
    '''
    for files in os.listdir(file('incomes')):
        file_path = os.path.join(file('incomes'), files)
        if os.path.isfile(file_path):
            os.unlink(file_path)
    print(f'\n{Fore.GREEN}» Incomes folder cleaned.')

    return


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

    utils = {
        'build_mail': (mail.mail_constructor, f'E-mail{Fore.WHITE}] Build e-mail from package in Incomes folder'),
        'page_gen': (page.page_gen, f'Form›LP{Fore.WHITE}] Swap or Add Form to a single Landing Page'),
        'campaign_gen': (campaign.campaign_gen, f'Campaign{Fore.WHITE}] Prepares Eloqua Campaign assets'),
        'webinar': (webinar.click_to_elq, f'Webinars{Fore.WHITE}] Upload Webinar registered users and attendees'),
        'database': (database.contact_list, f'Database{Fore.WHITE}] Create contact upload file with correct structure'),
        'clean_elq_track': (link.clean_elq_track, f'elqTrack{Fore.WHITE}] Delete elqTrack code in E-mail links'),
        'swap_utm_track': (link.swap_utm_track, f'utmTrack{Fore.WHITE}] Swap UTM tracking code in E-mail links'),
        'clean_outcomes': (clean_outcomes, f'Outcomes{Fore.WHITE}] Clean Outcomes folder'),
        'clean_incomes': (clean_incomes, f'Incomes{Fore.WHITE}] Clean Incomes folder'),
        'mail_groups': (corp.email_groups, f'Generator{Fore.WHITE}] Helper for GDPR Email Group Program')
    }

    # Access to all utils for admin
    if ELOQUA_USER == 'Mateusz.Dabrowski':
        available_utils = utils
    # Gets dict of utils available for users source country
    else:
        available_utils = {k: v for (k, v) in utils.items()
                           if k in COUNTRY_UTILS[SOURCE_COUNTRY]}
    util_names = list(available_utils.keys())

    print(f'\n{Fore.GREEN}ELQuent Utilites:')
    for i, function in enumerate(available_utils.values()):
        print(
            f'{Fore.WHITE}[{Fore.YELLOW}{i}{Fore.WHITE}]\t» [{Fore.YELLOW}{function[1]}')
    print(
        f'{Fore.WHITE}[{Fore.YELLOW}Q{Fore.WHITE}]\t» [{Fore.YELLOW}Quit{Fore.WHITE}]')

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
api.get_eloqua_auth(SOURCE_COUNTRY)

# Load domain and user name
ELOQUA_DOMAIN, ELOQUA_USER = pickle.load(open(file('eloqua'), 'rb'))

print(
    f'\n{Fore.YELLOW}User » {Fore.WHITE}[{Fore.GREEN}{ELOQUA_DOMAIN} {SOURCE_COUNTRY}{Fore.WHITE}] {ELOQUA_USER}')

# Checks for terminal arguments of shell function
if len(sys.argv) < 2:
    menu()
elif sys.argv[1] == 'track':
    link.clean_elq_track(SOURCE_COUNTRY)
elif sys.argv[1] == 'utm':
    link.swap_utm_track(SOURCE_COUNTRY)
elif sys.argv[1] == 'mail':
    mail.mail_constructor(SOURCE_COUNTRY)
elif sys.argv[1] == 'page':
    page.page_gen(SOURCE_COUNTRY)
elif sys.argv[1] == 'campaign':
    campaign.campaign_gen(SOURCE_COUNTRY)
elif sys.argv[1] == 'web':
    webinar.click_to_elq(SOURCE_COUNTRY)
elif sys.argv[1] == 'base':
    database.contact_list(SOURCE_COUNTRY)

# Allows to cycle through options after first errand
while True:
    menu()
