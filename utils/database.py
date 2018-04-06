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
        f'\n  {Fore.RED}[ATTENTION]{Fore.YELLOW} Currently supports only e-mail uploads')

    print(
        f'{Fore.WHITE}» [{Fore.YELLOW}CONTACTS{Fore.WHITE}] Copy list of e-mails [CTRL+C] and click [Enter]', end='')
    input(' ')
    database_content = pyperclip.paste()
    database_content = database_content.replace('\r\n', '\n')
    database_content = database_content.split('\n')

    # Builds .csv file in eloqua compliant structure
    count_contact = 0
    with open(file('database'), 'w') as f:
        fieldnames = ['Source_Country', 'Email Address']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for email in database_content:
            writer.writerow({
                'Source_Country': source_country,
                'Email Address': email
            })
            count_contact += 1
    print(
        f'\n{Fore.GREEN}» Database of {count_contact} contacts saved in Outcomes folder and ready to upload!',
        f'\n{Fore.WHITE}» Click [Enter] to continue.', end='')
    input(' ')

    return True


'''
TODO:
- Create function to add, trim and intersect databases
- Create validation of input
- Create functionality to work from .xls or .csv input
'''
