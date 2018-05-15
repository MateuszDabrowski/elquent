#!/usr/bin/env python3.6
# -*- coding: utf8 -*-

'''
ELQuent.corp
ELQuent helpers for central team

Mateusz Dąbrowski
github.com/MateuszDabrowski
linkedin.com/in/mateusz-dabrowski-marketing/
'''

# Python imports
import os
import sys
import json
from colorama import Fore, init

# ELQuent imports
import utils.api.api as api

# Initialize colorama
init(autoreset=True)

# Globals
naming = None
source_country = None

# Predefined messege elements
ERROR = f'{Fore.WHITE}[{Fore.RED}ERROR{Fore.WHITE}] {Fore.YELLOW}'
SUCCESS = f'{Fore.WHITE}[{Fore.GREEN}SUCCESS{Fore.WHITE}] '


def country_naming_setter(country):
    '''
    Sets source_country for all functions
    Loads json file with naming convention
    '''
    global source_country
    source_country = country

    # Loads json file with naming convention
    with open(file('naming'), 'r', encoding='utf-8') as f:
        global naming
        naming = json.load(f)


'''
=================================================================================
                            File Path Getter
=================================================================================
'''


def file(file_path, name='LP'):
    '''
    Returns file path to template files
    '''

    def find_data_file(filename, directory='templates'):
        '''
        Returns correct file path for both script and frozen app
        '''
        if directory == 'templates':  # For reading template files
            if getattr(sys, 'frozen', False):
                datadir = os.path.dirname(sys.executable)
            else:
                datadir = os.path.dirname(os.path.dirname(__file__))
            return os.path.join(datadir, 'utils', directory, filename)
        elif directory == 'api':  # For reading api files
            if getattr(sys, 'frozen', False):
                datadir = os.path.dirname(sys.executable)
            else:
                datadir = os.path.dirname(os.path.dirname(__file__))
            return os.path.join(datadir, 'utils', directory, filename)
        elif directory == 'outcomes':  # For writing outcome files
            if getattr(sys, 'frozen', False):
                datadir = os.path.dirname(sys.executable)
            else:
                datadir = os.path.dirname(os.path.dirname(__file__))
            return os.path.join(datadir, directory, filename)

    file_paths = {
        'naming': find_data_file('naming.json', directory='api'),
        'form': find_data_file(f'WKCORP_form-email-group.json'),
        'filter': find_data_file(f'WKCORP_filter-email-group.json'),
        'email-groups': find_data_file(f'WKCORP_email-groups.json'),
        'outcome-file': find_data_file(f'WK{source_country}_{name}.txt', directory='outcomes')
    }

    return file_paths.get(file_path)


'''
=================================================================================
                            Email Groups Program
=================================================================================
'''


def email_groups(country):
    '''
    Creates shared lists and forms for email group corp program
    '''

    def form_builder(countries, groups):
        '''
        Creates form for each given e-mail group
        '''
        # Prepares informations necessary for proper data in API call
        form_folder_id = countries['FolderID']['Form']

        # Gets form source json
        with open(file('form'), 'r', encoding='utf-8') as f:
            source_form_json = json.load(f)

        # Iterates for each e-mail group to create form for each
        for email_group in groups:
            print(
                f'\n{Fore.WHITE}[{Fore.YELLOW}CREATING{Fore.WHITE}] {email_group[0]} Form:')

            form_name = f'WK{source_country}_{email_group[0]}-{email_group[1]}_FORM'
            form_html_name = f'{email_group[0]}'

            # Change form json to string for easy replacing
            form_string = json.dumps(source_form_json)
            form_string = form_string\
                .replace('HTML_NAME', form_html_name)\
                .replace('FORM_NAME', form_name)\
                .replace('EMAIL_GROUP', email_group[0])\
                .replace('GROUP_ID', email_group[1])\
                .replace('FOLDER_ID', form_folder_id)

            # Change back to json for API call
            form_json = json.loads(form_string)

            # Creates form with given data
            form_id, form_response_json = api.eloqua_create_form(
                form_name, form_json)

            break

    def sharedfilter_builder(countries, groups):
        '''
        Creates pair of shared filters (sub/unsub) for each given e-mail group
        '''
        # Prepares informations necessary for proper data in API call
        filter_folder_id = countries['FolderID']['SharedFilter']

        # Gets form source json
        with open(file('filter'), 'r', encoding='utf-8') as f:
            source_filter_json = json.load(f)

        # Change form json to string for easy replacing
        filter_string = json.dumps(source_filter_json)

        # Iterates for each e-mail group to create form for each
        for email_group in groups:
            print(
                f'\n{Fore.WHITE}[{Fore.YELLOW}CREATING{Fore.WHITE}] {email_group[0]} Shared Filters (SUB/UNSUB):')

            # ---------------------------------- Creating Subscription Shared Filter
            filter_sub_name = f'WK{source_country}_{email_group[0]}-{email_group[1]}_SUB-FILTER'

            # Swapping shared filter elements
            filter_sub_string = filter_string\
                .replace('FILTER_NAME', filter_sub_name)\
                .replace('GROUP_ID', email_group[1])\
                .replace('FOLDER_ID', filter_folder_id)\
                .replace('SUB_CRITERION', 'SubscriptionCriterion')

            # Change back to json for API call
            filter_sub_json = json.loads(filter_sub_string)

            # Creates form with given data
            filter_id, filter_response_json = api.eloqua_create_filter(
                filter_sub_name, filter_sub_json)

            # ---------------------------------- Creating Unsubscription Shared Filter
            filter_unsub_name = f'WK{source_country}_{email_group[0]}-{email_group[1]}_UNSUB-FILTER'

            # Swapping shared filter elements
            filter_unsub_string = filter_string\
                .replace('FILTER_NAME', filter_unsub_name)\
                .replace('GROUP_ID', email_group[1])\
                .replace('FOLDER_ID', filter_folder_id)\
                .replace('SUB_CRITERION', 'UnsubscriptionCriterion')

            # Change back to json for API call
            filter_unsub_json = json.loads(filter_unsub_string)

            # Creates form with given data
            filter_id, filter_response_json = api.eloqua_create_filter(
                filter_unsub_name, filter_unsub_json)

            break

    # Create global source_country and load json file with naming convention
    country_naming_setter(country)

    # Loads json file with email groups
    with open(file('email-groups'), 'r', encoding='utf-8') as f:
        countries = json.load(f)
    countries_list = list(countries.keys())[1:]

    # Prints countires available in json file
    print(f'\n{Fore.GREEN}Countries available in json:')
    for i, country in enumerate(countries_list):
        print(
            f'{Fore.WHITE}[{Fore.YELLOW}{i}{Fore.WHITE}]\t» [{Fore.YELLOW}{country}{Fore.WHITE}]')
    print(
        f'{Fore.WHITE}[{Fore.YELLOW}Q{Fore.WHITE}]\t» [{Fore.YELLOW}Quit{Fore.WHITE}]')

    # Allows user to choose which country assets he wants to generate
    while True:
        print(
            f'{Fore.YELLOW}Enter number associated with chosen country:', end='')
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
        if 0 <= choice < len(country):
            break
        else:
            print(f'{Fore.RED}Entered value does not belong to any country!')
            choice = ''

    # Modifies chosen country to a list of tuples
    groups = countries.get(countries_list[choice])
    groups = list(groups.items())

    form_builder(countries, groups)
    sharedfilter_builder(countries, groups)

    # TODO Check how canvas creation API works

    return