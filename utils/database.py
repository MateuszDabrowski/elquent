#!/usr/bin/env python3.6
# -*- coding: utf8 -*-

'''
ELQuent.database
Creates database in Eloqua compliant structure from user input

Mateusz Dąbrowski
github.com/MateuszDabrowski
linkedin.com/in/mateusz-dabrowski-marketing/
'''

# Python imports
import os
import re
import csv
import sys
import json
import pyperclip
from colorama import Fore, init

# ELQuent imports
import utils.api.api as api

# Initialize colorama
init(autoreset=True)

# Predefined messege elements
ERROR = f'{Fore.RED}  [ERROR] {Fore.YELLOW}'

'''
=================================================================================
                            File Path Getter
=================================================================================
'''


def file(file_path, name=''):
    '''
    Returns file path to template files
    '''

    def find_data_file(filename, dir):
        '''
        Returns correct file path for both script and frozen app
        '''
        if dir == 'api':  # For reading api files
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
        'naming': find_data_file('naming.json', dir='api'),
        'database': find_data_file(f'{name}.txt', dir='outcomes')
    }

    return file_paths.get(file_path)


'''
=================================================================================
                                User input functions
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
                                Eloqua upload functions
=================================================================================
'''


def upload_to_eloqua(contacts):
    '''
    Uploads contact list to Eloqua as a shared list
    Returns campaign name
    '''

    # Gets campaign name from user
    while True:
        print(
            f'\n{Fore.WHITE}» [{Fore.YELLOW}NAME{Fore.WHITE}] Copy name for the shared list [CTRL+C] and click [Enter]', end='')
        input(' ')
        campaign_name = pyperclip.paste()
        campaign_name_check = campaign_name.split('_')
        if len(campaign_name_check) != 5:
            print(
                f'{ERROR}Expected 5 name elements, found {len(campaign_name_check)}')
        elif campaign_name_check[0][:2] != 'WK':
            print(
                f'{ERROR}"{campaign_name_check[0]}" is not existing country code')
        elif campaign_name_check[1] not in naming[source_country]['segment']:
            print(
                f'{ERROR}"{campaign_name_check[1]}" is not existing segment name')
        elif campaign_name_check[2] not in naming['campaign']:
            print(
                f'{ERROR}"{campaign_name_check[2]}" is not existing campaign type')
        else:
            break

    # Cleans contact list from non-email elements
    contacts = [x for x in contacts if '@' in x and '.' in x]

    uploading = ''
    while uploading.lower() != 'y' and uploading.lower() != 'n':
        # Prepares dict for import
        contacts_to_upload = {campaign_name: contacts}
        # Confirms if everything is correct
        print(
            f'\n{Fore.YELLOW}» {Fore.WHITE}Import {Fore.YELLOW}{len(contacts)}{Fore.WHITE} contacts to {Fore.YELLOW}{campaign_name}{Fore.WHITE} shared list? {Fore.CYAN}(Y/N or write new ending to change list name):', end='')
        uploading = input(' ')
        if len(uploading) > 1:
            campaign_name = '_'.join(campaign_name_check[:4] + [uploading])
    if uploading.lower() == 'y':
        api.upload_contacts(source_country, contacts_to_upload, 'database')

    return campaign_name


'''
=================================================================================
                                Main program flow
=================================================================================
'''


def contact_list(country):
    '''
    Takes copied database and transforms it into .csv file
    compliant with Eloqua for manual import.
    '''

    # Create global source_country from main module
    global source_country
    source_country = country

    # Loads json file with naming convention
    with open(file('naming'), 'r', encoding='utf-8') as f:
        global naming
        naming = json.load(f)

    # Gets contact list from user
    contacts = get_contacts()

    options = [
        f'{Fore.WHITE}[{Fore.YELLOW}NO{Fore.WHITE}] Save current contact list',
        f'{Fore.WHITE}[{Fore.YELLOW}TRIM{Fore.WHITE}] Delete new emails from previosly uploaded list',
        f'{Fore.WHITE}[{Fore.YELLOW}APPEND{Fore.WHITE}] Add new emails to previously uploaded list',
        f'{Fore.WHITE}[{Fore.YELLOW}INTERSECT{Fore.WHITE}] Leave only emails existing in both old and new list'
    ]
    # Asks users if he wants to manipulate data set
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

    # Asks if user want to upload contacts to Eloqua
    name = ''
    if naming[source_country]['api']['bulk'] == 'enabled':
        swapping = ''
        while swapping.lower() != 'y' and swapping.lower() != 'n':
            print(
                f'\n{Fore.WHITE}» [{Fore.YELLOW}UPLOAD{Fore.WHITE}] Do you want to upload that list to Eloqua? (Y/N):', end='')
            swapping = input(' ')
        if swapping.lower() == 'y':
            name = upload_to_eloqua(contacts)
    name = f'WK{source_country}_Contact-Upload' if not name else name

    # Builds .csv file in eloqua compliant structure
    count_contact = 0
    with open(file('database', name), 'w') as f:
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
        f'\n{Fore.GREEN}Database of {count_contact} contacts saved in Outcomes folder.')

    # Asks user if he would like to repeat
    print(
        f'{Fore.WHITE}» Do you want to prepare another contact upload? (Y/N)', end='')
    choice = input(' ')
    if choice.lower() == 'y':
        contact_list(country)
    else:
        print(
            f'\n{Fore.GREEN}-----------------------------------------------------------------------------')
        return True


'''
TODO:
- Create validation of input
- Create functionality to work from .xls or .csv input
'''
