#!/usr/bin/env python3.6
# -*- coding: utf8 -*-

'''
ELQuent.database
Creates database in Eloqua compliant structure from user input

Mateusz Dąbrowski
github.com/MateuszDabrowski
linkedin.com/in/mateusz-dabrowski-marketing/
'''

import os
import csv
import sys
import pyperclip
from colorama import Fore, init

# Initialize colorama
init(autoreset=True)


def file(file_path, name='LP'):
    '''
    Returns file path to template files
    '''

    def find_data_file(filename, dir='templates'):
        '''
        Returns correct file path for both script and frozen app
        '''
        if dir == 'templates':  # For reading template files
            if getattr(sys, 'frozen', False):
                datadir = os.path.dirname(sys.executable)
            else:
                datadir = os.path.dirname(os.path.dirname(__file__))
            return os.path.join(datadir, 'utils', dir, filename)
        elif dir == 'outcomes':  # For writing outcome files
            if getattr(sys, 'frozen', False):
                datadir = os.path.dirname(sys.executable)
            else:
                datadir = os.path.dirname(os.path.dirname(__file__))
            return os.path.join(datadir, dir, filename)

    file_paths = {
        'database': find_data_file(f'WK{source_country}_Contact-Upload.txt', dir='outcomes')
    }

    return file_paths.get(file_path)


'''
=================================================================================
                            Input functions
=================================================================================
'''


def get_contacts():
    '''
    Returns contact list from user input
    '''
    print(
        f'\n{Fore.WHITE}» [{Fore.YELLOW}CONTACTS{Fore.WHITE}] Copy list of e-mails [CTRL+C] and click [Enter]', end='')
    input(' ')
    database = pyperclip.paste()

    # Removes possible whitespace characters
    database = database.replace('\r\n', '\n')

    # Translates input into a list
    database = database.split('\n')

    # Takes care of empty line at the end of input
    if database[-1] == '':
        database.pop()

    # Deduplicates list
    database = list(set(database))
    print(
        f'{Fore.WHITE}  [{Fore.GREEN}UPLOADED{Fore.WHITE}] {len(database)} unique e-mails uploaded')

    return database


'''
=================================================================================
                                Main program flow
=================================================================================
'''


def create_csv(country):
    '''
    Takes copied database and transforms it into .csv file
    compliant with Eloqua for manual import.
    '''

    # Create global source_country from main module
    global source_country
    source_country = country

    # Gets contact list from user
    print(
        f'\n  {Fore.RED}[ATTENTION]{Fore.YELLOW} Currently only support upload of e-mails')
    contacts = get_contacts()

    options = [
        f'{Fore.WHITE}[{Fore.YELLOW}NO{Fore.WHITE}] Create .csv',
        f'{Fore.WHITE}[{Fore.YELLOW}TRIM{Fore.WHITE}] Delete new emails from previosly uploaded list',
        f'{Fore.WHITE}[{Fore.YELLOW}APPEND{Fore.WHITE}] Add new emails to previously uploaded list',
        f'{Fore.WHITE}[{Fore.YELLOW}INTERSECT{Fore.WHITE}] Leave only emails existing in both old and new list'
    ]

    while True:
        print(f'\n{Fore.GREEN}Do you want to add, trim or intersect another list?')
        for i, option in enumerate(options):
            print(f'{Fore.WHITE}[{Fore.YELLOW}{i}{Fore.WHITE}]\t{option}')
        print(f'{Fore.YELLOW}Enter number associated with your choice:', end='')
        choice = input(' ')
        if choice == '0' or not choice:
            break
        elif choice == '1':
            new_contacts = get_contacts()
            contacts = [x for x in contacts if x not in new_contacts]
        elif choice == '2':
            new_contacts = get_contacts()
            contacts.extend(new_contacts)
            contacts = list(set(contacts))
        elif choice == '3':
            new_contacts = get_contacts()
            contacts = [x for x in contacts if x in new_contacts]
        else:
            print(f'{Fore.RED}Entered value does not belong to any option!')
            continue
        print(
            f'\n{Fore.WHITE}» [{Fore.GREEN}SUCCESS{Fore.WHITE}] New database got {len(contacts)} unique e-mails')

    # Builds .csv file in eloqua compliant structure
    count_contact = 0
    with open(file('database'), 'w') as f:
        fieldnames = ['Source_Country', 'Email Address']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for email in contacts:
            if '@' not in email:
                continue
            writer.writerow({
                'Source_Country': source_country,
                'Email Address': email
            })
            count_contact += 1
    print(
        f'\n{Fore.GREEN}» Database of {count_contact} contacts saved in Outcomes folder and ready to upload!',
        f'\n{Fore.WHITE}» Click [Enter] to continue.', end='')
    input(' ')

    print(f'\n{Fore.GREEN}-----------------------------------------------------------------------------')

    return True


'''
TODO:
- Create validation of input
- Add import to Eloqua functionality
- Create functionality to work from .xls or .csv input
'''
