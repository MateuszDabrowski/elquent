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
from colorama import Fore, Style, init

# ELQuent imports
import utils.api.api as api

# Initialize colorama
init(autoreset=True)

# Predefined messege elements
ERROR = f'{Fore.WHITE}[{Fore.RED}ERROR{Fore.WHITE}] {Fore.YELLOW}'
SUCCESS = f'{Fore.WHITE}[{Fore.GREEN}SUCCESS{Fore.WHITE}] '

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
    while True:
        print(
            f'\n{Fore.WHITE}» [{Fore.YELLOW}CONTACTS{Fore.WHITE}] Copy list of e-mails [CTRL+C] and click [Enter]', end='')
        input(' ')
        database = pyperclip.paste()

        # Removes possible whitespace characters
        database = database.replace('\r\n', '\n')

        # Translates input into a list
        database = database.split('\n')

        # Checks sample of import to validate data
        validate_database = ';'.join(database) + ';'
        valid_mail = re.compile(
            r'([\w\.\-\+]+?@[\w\.\-\+]+?\.[\w\.\-\+]+?);', re.UNICODE)
        validated_mails = valid_mail.findall(validate_database)

        # Takes care of empty line at the end of input
        if database[-1] == '':
            database.pop()

        # Informs user about invalid upload
        if len(database) > len(validated_mails):
            print(
                f'\n{ERROR}Out of {len(database)} records uploaded, {len(validated_mails)} are correct e-mails.',
                f'\n  {Fore.WHITE}» Show incorrect ones? ({Style.BRIGHT}{Fore.GREEN}y{Fore.WHITE}/{Fore.RED}n{Fore.WHITE}{Style.NORMAL}):', end='')
            print_diff = input(' ')
            if print_diff.lower() == 'y':  # Allows user to see which particular lines are incorrect
                diff = [mail for mail in database if mail not in validated_mails]
                print(diff)
            elif print_diff.lower() == 'i':  # Allows to ignore validation
                break
            print(
                f'\n{Fore.WHITE}Please copy a list containing only e-mail address in each line', end='')
            continue
        else:
            break

    # Deduplicates list
    database = list(set(database))
    print(
        f'{Fore.WHITE}  [{Fore.GREEN}ADDED{Fore.WHITE}] {len(database)} unique e-mails added')

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
    print(
        f'\n{Fore.WHITE}» [{Fore.YELLOW}NAME{Fore.WHITE}] Write or paste name for the shared list and click [Enter]')
    campaign_name = api.eloqua_asset_name()

    # Cleans contact list from non-email elements
    contacts = [x for x in contacts if '@' in x and '.' in x]

    uploading = ''
    while uploading.lower() != 'y' and uploading.lower() != 'n':
        # Prepares dict for import
        contacts_to_upload = {campaign_name: contacts}
        # Confirms if everything is correct
        print(
            f'\n{Fore.YELLOW}» {Fore.WHITE}Import {Fore.YELLOW}{len(contacts)}{Fore.WHITE} contacts to {Fore.YELLOW}{campaign_name}{Fore.WHITE} shared list?',
            f'\n{Fore.WHITE}({Style.BRIGHT}{Fore.GREEN}y{Fore.WHITE}/{Fore.RED}n{Fore.WHITE}{Style.NORMAL} or {Fore.YELLOW}write{Fore.WHITE} new ending to change list name):', end='')
        uploading = input(' ')
        if len(uploading) > 1:
            campaign_name = '_'.join(
                (campaign_name.split('_'))[:-1] + [uploading])
    if uploading.lower() == 'y':
        api.upload_contacts(contacts_to_upload, list_type='upload')

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
        f'{Fore.WHITE}[{Fore.YELLOW}UPLOAD{Fore.WHITE}] Contact list ready to be saved',
        f'{Fore.WHITE}[{Fore.YELLOW}TRIM{Fore.WHITE}] Delete new emails from previosly uploaded list',
        f'{Fore.WHITE}[{Fore.YELLOW}APPEND{Fore.WHITE}] Add new emails to previously uploaded list',
        f'{Fore.WHITE}[{Fore.YELLOW}INTERSECT{Fore.WHITE}] Leave only emails existing in both old and new list'
    ]
    # Asks users if he wants to manipulate data set
    while True:
        print(
            f'\n{Fore.GREEN}Do you want to upload list or add, trim or intersect with another one?')
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
                f'\n{Fore.WHITE}» [{Fore.YELLOW}UPLOAD{Fore.WHITE}] Do you want to upload that list to Eloqua? ({Style.BRIGHT}{Fore.GREEN}y{Fore.WHITE}/{Fore.RED}n{Fore.WHITE}{Style.NORMAL}):', end='')
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
        f'{Fore.WHITE}» Do you want to prepare another contact upload? ({Style.BRIGHT}{Fore.GREEN}y{Fore.WHITE}/{Fore.RED}n{Fore.WHITE}{Style.NORMAL})', end='')
    choice = input(' ')
    if choice.lower() == 'y':
        print(
            f'\n{Fore.GREEN}-----------------------------------------------------------------------------')
        contact_list(country)

    return
