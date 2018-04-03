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
    source_country_list = [
        'AK', 'BE', 'CZ', 'DE', 'ES', 'FR',
        'HU', 'IT', 'LSW', 'NL', 'PL', 'SK'
    ]
    for i, country in enumerate(source_country_list):
        print(
            f'{Fore.WHITE}[{Fore.YELLOW}{i}{Fore.WHITE}]\t{Fore.GREEN}WK{Fore.WHITE}{country}')

    while True:
        print(f'{Fore.WHITE}Enter number associated with you country: ', end='')
        try:
            source_country = int(input(' '))
        except ValueError:
            print(f'{Fore.RED}Please enter numeric value!')
            continue
        if 0 <= source_country < len(source_country_list):
            break
        else:
            print(f'{Fore.RED}Entered value does not belong to any country!')

    return source_country_list[source_country]


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

    utils = [
        (mail.clean_elq_track,
         f'{Fore.WHITE}[{Fore.YELLOW}MAIL{Fore.WHITE}] Delete elqTrack code in Email links'),
        (mail.swap_utm_track,
         f'{Fore.WHITE}[{Fore.YELLOW}MAIL{Fore.WHITE}] Swap UTM tracking code in Email links'),
        (page.page_gen,
         f'{Fore.WHITE}[{Fore.YELLOW}PAGE{Fore.WHITE}] Create or modify single Landing Page with new Form'),
        (page.campaign_gen,
         f'{Fore.WHITE}[{Fore.YELLOW}PAGE{Fore.WHITE}] Create set of Landing Pages for whole campaign')
    ]

    print(f'\n{Fore.GREEN}ELQuent Utilites:')
    for i, function in enumerate(utils):
        print(f'{Fore.WHITE}[{Fore.YELLOW}{i}{Fore.WHITE}]\t{function[1]}')
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
        if 0 <= choice < len(utils):
            break
        else:
            print(f'{Fore.RED}Entered value does not belong to any utility!')
    utils[choice][0](SOURCE_COUNTRY)


'''
=================================================================================
                                Main program flow
=================================================================================
'''
print(f'\n{Fore.GREEN}Ahoj!')

# Checks if there is newer version of the app
if new_version():
    print(f'\n{Fore.WHITE}[{Fore.RED}!{Fore.WHITE}] Newer version available')

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
- Storing countries and utils in json
- Printing utils based on country and eloqua auth
'''