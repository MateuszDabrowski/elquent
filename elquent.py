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
import pickle
import requests
import encodings
from colorama import Fore, init

# ELQuent imports
import utils.mail as mail
import utils.page as page
import utils.webinar as webinar
import utils.database as database
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

    def find_data_file(filename, dir='main'):
        '''
        Returns correct file path for both script and frozen app
        '''
        if dir == 'main':  # Files in main directory
            if getattr(sys, 'frozen', False):
                datadir = os.path.dirname(sys.executable)
            else:
                datadir = os.path.dirname(os.path.dirname(__file__))
            return os.path.join(datadir, filename)
        elif dir == 'api':  # Auths saved in api directory
            if getattr(sys, 'frozen', False):
                datadir = os.path.dirname(sys.executable)
            else:
                datadir = os.path.dirname(os.path.dirname(__file__))
            return os.path.join(datadir, 'utils', dir, filename)

    file_paths = {
        'outcomes': find_data_file('outcomes'),
        'utils': find_data_file('utils.json'),
        'readme': find_data_file('readme.md'),
        'country': find_data_file('country.p', dir='api'),
        'eloqua': find_data_file('eloqua.p', dir='api')
    }

    return file_paths.get(file_path)


# Builds folder for outcomes
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
    with open(file('readme'), 'r', encoding='utf-8') as f:
        readme = f.read()
    check_current_version = re.compile(r'\[_Version: (.*?)_\]', re.UNICODE)
    current_version = check_current_version.findall(readme)

    # Gets available version number on Github
    github = requests.get('https://github.com/MateuszDabrowski/ELQuent')
    check_available_version = re.compile(
        r'\[<em>Version: (.*?)</em>\]', re.UNICODE)
    available_version = check_available_version.findall(github.text)

    # Compares versions
    if current_version and available_version and current_version[0] != available_version[0]:
        return True
    else:
        return False


'''
=================================================================================
                            Cleans Outcomes folder
=================================================================================
'''


def clean_outcomes(country):
    '''
    Cleans all content of Outcomes folder
    '''
    for f in os.listdir(file('outcomes')):
        file_path = os.path.join(file('outcomes'), f)
        if os.path.isfile(file_path):
            os.unlink(file_path)
    print(f'\n{Fore.GREEN}» Outcomes folder cleaned.')

    print(f'\n{Fore.GREEN}-----------------------------------------------------------------------------')
    return True


'''
=================================================================================
                                    Main menu
=================================================================================
'''


def menu(choice=''):
    '''
    Allows to choose ELQuent utility
    '''
    utils = {
        'clean_outcomes': (clean_outcomes, f'Clean Outcomes folder'),
        'clean_elq_track': (mail.clean_elq_track, f'Delete elqTrack{Fore.WHITE} code in Email links'),
        'swap_utm_track': (mail.swap_utm_track, f'Swap UTM{Fore.WHITE} tracking code in Email links'),
        'page_gen': (page.page_gen, f'Swap or Add Form{Fore.WHITE} to a single Landing Page'),
        'campaign_gen': (page.campaign_gen, f'Prepare Campaign{Fore.WHITE} required set of Landing Pages'),
        'database': (database.create_csv, f'Create contact upload{Fore.WHITE} file with correct structure'),
        'webinar': (webinar.click_to_elq, f'Upload Webinar{Fore.WHITE} registered users and attendees')
    }

    # Gets dict of utils available for users source country
    available_utils = {k: v for (k, v) in utils.items()
                       if k in COUNTRY_UTILS[SOURCE_COUNTRY]}
    util_names = list(available_utils.keys())

    print(f'\n{Fore.GREEN}ELQuent Utilites:')
    for i, function in enumerate(available_utils.values()):
        print(
            f'{Fore.WHITE}[{Fore.YELLOW}{i}{Fore.WHITE}]\t» {Fore.YELLOW}{function[1]}')
    print(f'{Fore.WHITE}[{Fore.YELLOW}Q{Fore.WHITE}]\t{Fore.WHITE}Quit')

    while True:
        if not choice:
            print(
                f'{Fore.YELLOW}Enter number associated with choosen utility:', end='')
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

# Loads domain and user name
if os.path.isfile(file('eloqua')):
    ELOQUA_DOMAIN, ELOQUA_USER = pickle.load(open(file('eloqua'), 'rb'))
else:
    ELOQUA_DOMAIN = 'WK'
    ELOQUA_USER = ''

# Gets required auth data and prints them
SOURCE_COUNTRY = get_source_country()
print(
    f'\n{Fore.YELLOW}User » {Fore.WHITE}[{Fore.GREEN}{ELOQUA_DOMAIN} {SOURCE_COUNTRY}{Fore.WHITE}] {ELOQUA_USER}')

# Checks for terminal arguments of shell function
if len(sys.argv) < 2:
    menu()
elif sys.argv[1] == 'track':
    mail.clean_elq_track(SOURCE_COUNTRY)
elif sys.argv[1] == 'utm':
    mail.swap_utm_track(SOURCE_COUNTRY)
elif sys.argv[1] == 'page':
    page.page_gen(SOURCE_COUNTRY)
elif sys.argv[1] == 'campaign':
    page.campaign_gen(SOURCE_COUNTRY)
elif sys.argv[1] == 'web':
    webinar.click_to_elq(SOURCE_COUNTRY)
elif sys.argv[1] == 'base':
    database.create_csv(SOURCE_COUNTRY)

# Allows to cycle through options after first errand
while True:
    menu()
