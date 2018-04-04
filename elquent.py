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
import pyperclip
from colorama import Fore, init

# ELQuent imports
import utils.mail as mail
import utils.page as page

# Initialize colorama
init(autoreset=True)


def find_data_file(filename):
    '''
    Returns correct file path for both script and frozen app
    '''
    if getattr(sys, 'frozen', False):
        datadir = os.path.dirname(sys.executable)
    else:
        datadir = os.path.dirname(__file__)
    return os.path.join(datadir, filename)


# File paths
os.makedirs(find_data_file('outcomes'), exist_ok=True)
USER_DATA = find_data_file('user.p')
README = find_data_file('README.md')
UTILS = find_data_file('utils.json')


'''
=================================================================================
                            Authentication functions
=================================================================================
'''


def get_source_country():
    '''
    Returns source country of the user from input
    » source_country: two char str
    '''
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

    return source_country_list[choice]


def auth_pickle():
    '''
    Returns authenticaton data from shelve
    » source_country: two char str
    '''
    if not os.path.isfile(USER_DATA):
        source_country = get_source_country()
        pickle.dump(source_country, open(USER_DATA, 'wb'))
    source_country = pickle.load(open(USER_DATA, 'rb'))

    return source_country


def new_version():
    '''
    Returns True if there is newer version of the app available
    '''
    # Gets current version number of running app
    with open(README, 'r', encoding='utf-8') as f:
        readme = f.read()
    check_current_version = re.compile(r'\[_Version: (.*?)_\]', re.UNICODE)
    current_version = check_current_version.findall(readme)

    # Gets available version number on Github
    github = requests.get('https://github.com/MateuszDabrowski/ELQuent')
    check_available_version = re.compile(r'\[<em>Version: (.*?)</em>\]', re.UNICODE)
    available_version = check_available_version.findall(github.text)

    # Compares versions
    if current_version and available_version and current_version[0] != available_version[0]:
        return True
    else:
        return False


'''
=================================================================================
                            Authentication functions
=================================================================================
'''


def menu():
    '''
    Allows to choose ELQuent utility 
    '''
    utils = {
        'clean_elq_track': (mail.clean_elq_track, f'Delete elqTrack{Fore.WHITE} code in Email links'),
        'swap_utm_track': (mail.swap_utm_track, f'Swap UTM{Fore.WHITE} tracking code in Email links'),
        'page_gen': (page.page_gen, f'Swap or Add Form{Fore.WHITE} to a single Landing Page'),
        'campaign_gen': (page.campaign_gen, f'Prepare Campaign{Fore.WHITE} required set of Landing Pages')
    }

    # Gets dict of utils available for users source country
    available_utils = {k:v for (k, v) in utils.items() if k in COUNTRY_UTILS[SOURCE_COUNTRY]}
    util_names = list(available_utils.keys())

    print(f'\n{Fore.GREEN}ELQuent Utilites:')
    for i, function in enumerate(available_utils.values()):
        print(f'{Fore.WHITE}[{Fore.YELLOW}{i}{Fore.WHITE}]\t» {Fore.YELLOW}{function[1]}')
    print(f'{Fore.WHITE}[{Fore.YELLOW}Q{Fore.WHITE}]\t{Fore.WHITE}Quit')

    while True:
        print(f'{Fore.YELLOW}Enter number associated with choosen utility:', end='')
        choice = input(' ')
        if choice.lower() == 'q':
            print(f'\n{Fore.GREEN}Ahoj!')
            raise SystemExit
        try:
            choice = int(choice)
        except ValueError:
            print(f'{Fore.RED}Please enter numeric value!')
            continue
        if 0 <= choice < len(available_utils):
            break
        else:
            print(f'{Fore.RED}Entered value does not belong to any utility!')
    available_utils.get(util_names[choice])[0](SOURCE_COUNTRY)


'''
=================================================================================
                                Main program flow
=================================================================================
'''
print(f'\n{Fore.GREEN}Ahoj!')

# Checks if there is newer version of the app
if new_version():
    print(f'\n{Fore.WHITE}[{Fore.RED}!{Fore.WHITE}]{Fore.RED} Newer version available')

# Loads utils.json containing source countries and utils available for them
with open(UTILS, 'r', encoding='utf-8') as f:
    COUNTRY_UTILS = json.load(f)

# Gets required auth data and prints them
SOURCE_COUNTRY = auth_pickle()
print(
    f'\n{Fore.YELLOW}User » {Fore.WHITE}[{Fore.GREEN}WK{SOURCE_COUNTRY}{Fore.WHITE}]')

# Menu for choosing utils
while True:
    menu()

'''
TODO:
- Eloqua authentication
'''