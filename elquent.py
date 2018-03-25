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
import sys
import shelve
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
USER_DATA = find_data_file('user.db')

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


def auth_shelve():
    '''
    Returns authenticaton data from shelve
    » source_country: two char str
    '''
    with shelve.open(USER_DATA[:-3]) as auth_file:
        source_country = auth_file['SourceCountry']
    return source_country


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
        (mail.clean_elqtrack,
         f'{Fore.WHITE}[{Fore.YELLOW}MAIL{Fore.WHITE}] Delete elqTrack code from Email links'),
        (page.page_gen,
         f'{Fore.WHITE}[{Fore.YELLOW}PAGE{Fore.WHITE}] Create or modify Landing Page with new Form')
    ]

    print(f'\n{Fore.GREEN}ELQuent Utilites:')
    for i, function in enumerate(utils):
        print(f'{Fore.WHITE}[{Fore.YELLOW}{i}{Fore.WHITE}]\t{function[1]}')
    print(f'{Fore.WHITE}[{Fore.YELLOW}Q{Fore.WHITE}]\t{Fore.WHITE}Quit')

    while True:
        choice = input(
            f'{Fore.YELLOW}Enter number associated with choosen utility: ')
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

# Gets required auth data
if not os.path.isfile(USER_DATA):
    SOURCE_COUNTRY = get_source_country()
    with shelve.open(USER_DATA[:-3]) as auth_file:
        auth_file['SourceCountry'] = SOURCE_COUNTRY
SOURCE_COUNTRY = auth_shelve()
print(
    f'\n{Fore.YELLOW}User » {Fore.WHITE}[{Fore.GREEN}WK{SOURCE_COUNTRY}{Fore.WHITE}]')

# Menu for choosing utils
while True:
    menu()
