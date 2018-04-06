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
import base64
import pickle
import getpass
import requests
import encodings
import pyperclip
from colorama import Fore, init

# ELQuent imports
import utils.mail as mail
import utils.page as page
import utils.webinar as webinar
import utils.database as database

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
COUNTRY = find_data_file('country.p')
ELOQUA = find_data_file('eloqua.p')
CLICK = find_data_file('click.p')
README = find_data_file('README.md')
UTILS = find_data_file('utils.json')


'''
=================================================================================
                            Authentication functions
=================================================================================
'''


def get_source_country():
    '''
    Returns source country either from the user input or shelve
    » source_country: two char str
    '''
    if not os.path.isfile(COUNTRY):
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
        pickle.dump(source_country, open(COUNTRY, 'wb'))
    source_country = pickle.load(open(COUNTRY, 'rb'))

    return source_country


def get_click_auth():
    '''
    Returns ClickMeeting API Key needed for authorization
    '''
    if not os.path.isfile(CLICK):
        print(
            f'\n{Fore.WHITE}Copy ClickMeeting API Key [CTRL+C] and click [Enter]', end='')
        input(' ')
        click_api_key = pyperclip.paste()
        pickle.dump(click_api_key, open(CLICK, 'wb'))
    click_api_key = pickle.load(open(CLICK, 'rb'))

    return click_api_key


def get_eloqua_auth():
    '''
    Returns:
    1. Eloqua API Key needed for authorization.
    2. Eloqua Root URL
    3. User name
    '''
    def get_eloqua_root(eloqua_auth):
        '''
        Returns Eloqua base URL for your instance.
        '''
        root = 'https://login.eloqua.com/id'
        response = webinar.api_request(root=root, eloqua_auth=eloqua_auth)
        base_url = response.json()
        base_url = base_url['urls']['base']

        return base_url

    while True:
        # Gets Eloqua user details if they are already stored
        if not os.path.isfile(ELOQUA):
            print(f'{Fore.YELLOW}» {Fore.WHITE}Enter Eloqua Company name: ', end='')
            eloqua_domain = input(' ')
            print(f'{Fore.YELLOW}» {Fore.WHITE}Enter Eloqua User name: ', end='')
            eloqua_user = input(' ')
            eloqua_auth = (eloqua_domain, eloqua_user)
            pickle.dump(eloqua_auth, open(ELOQUA, 'wb'))
        eloqua_domain, eloqua_user = pickle.load(open(ELOQUA, 'rb'))
        eloqua_password = getpass.getpass(
            f'{Fore.YELLOW}» {Fore.WHITE}Enter Eloqua Password: ')

        # Converts domain, user and  to Eloqua Auth Key
        eloqua_api_key = bytes(eloqua_domain + '\\' +
                               eloqua_user + ':' +
                               eloqua_password, 'utf-8')
        eloqua_api_key = str(base64.b64encode(eloqua_api_key), 'utf-8')

        # Gets Eloqua root URL
        try:
            eloqua_root = get_eloqua_root(eloqua_api_key)
        except TypeError:
            print(f'{Fore.RED}[ERROR] {Fore.YELLOW}Login failed!')
            os.remove(ELOQUA)
            continue
        if eloqua_root:
            break

    return (eloqua_api_key, eloqua_root)


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
                            Authentication functions
=================================================================================
'''


def menu(choice=''):
    '''
    Allows to choose ELQuent utility
    '''
    utils = {
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

    while not choice:
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
    if util_names[choice] == 'webinar':
        click_auth = get_click_auth()
        eloqua_key, eloqua_root = get_eloqua_auth()
        available_utils.get(util_names[choice])[0](
            SOURCE_COUNTRY, click_auth, eloqua_key, eloqua_root)
    else:
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
with open(UTILS, 'r', encoding='utf-8') as f:
    COUNTRY_UTILS = json.load(f)

# Loads
if os.path.isfile(ELOQUA):
    ELOQUA_DOMAIN, ELOQUA_USER = pickle.load(open(ELOQUA, 'rb'))
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
    click_auth = get_click_auth()
    eloqua_key, eloqua_root = get_eloqua_auth()
    webinar.click_to_elq(SOURCE_COUNTRY, click_auth, eloqua_key, eloqua_root)
elif sys.argv[1] == 'base':
    database.create_csv(SOURCE_COUNTRY)

# Allows to cycle through options after first errand
while True:
    menu()

'''
TODO:
- check if eloqua user data is available for logged in users
'''
