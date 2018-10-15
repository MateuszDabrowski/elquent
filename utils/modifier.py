#!/usr/bin/env python3.6
# -*- coding: utf8 -*-

'''
ELQuent.modifier
Massive modification suite for multiple assets

Mateusz Dąbrowski
github.com/MateuszDabrowski
linkedin.com/in/mateusz-dabrowski-marketing/
'''

# Python imports
import os
import re
import sys
import json
import pyperclip
from colorama import Fore, Style, init

# ELQuent imports
import utils.api.api as api
import utils.helper as helper

# Initialize colorama
init(autoreset=True)

# Globals
naming = None
source_country = None

# Predefined messege elements
ERROR = f'{Fore.WHITE}[{Fore.RED}ERROR{Fore.WHITE}] {Fore.YELLOW}'
WARNING = f'{Fore.WHITE}[{Fore.YELLOW}WARNING{Fore.WHITE}] '
SUCCESS = f'{Fore.WHITE}[{Fore.GREEN}SUCCESS{Fore.WHITE}] '
YES = f'{Style.BRIGHT}{Fore.GREEN}y{Fore.WHITE}{Style.NORMAL}'
NO = f'{Style.BRIGHT}{Fore.RED}n{Fore.WHITE}{Style.NORMAL}'


def country_naming_setter(country):
    '''
    Sets source_country for all functions
    Loads json file with naming convention
    '''
    global source_country
    source_country = country

    # Prepares globals for imported modules
    helper.country_naming_setter(source_country)

    # Loads json file with naming convention
    with open(file('naming'), 'r', encoding='utf-8') as f:
        global naming
        naming = json.load(f)


'''
=================================================================================
                            File Path Getter
=================================================================================
'''


def file(file_path, name=''):
    '''
    Returns file path to template files
    '''

    def find_data_file(filename, directory):
        '''
        Returns correct file path for both script and frozen app
        '''
        if directory == 'outcomes':  # For saving outcomes
            if getattr(sys, 'frozen', False):
                datadir = os.path.dirname(sys.executable)
            else:
                datadir = os.path.dirname(os.path.dirname(__file__))
            return os.path.join(datadir, directory, filename)
        elif directory == 'api':  # For writing auth files
            if getattr(sys, 'frozen', False):
                datadir = os.path.dirname(sys.executable)
            else:
                datadir = os.path.dirname(os.path.dirname(__file__))
            return os.path.join(datadir, 'utils', directory, filename)

    file_paths = {
        'naming': find_data_file('naming.json', directory='api'),
        'outcome-json': find_data_file(f'WK{source_country}_{name}.json', directory='outcomes'),
        'outcome-csv': find_data_file(f'WK{source_country}_{name}.csv', directory='outcomes')
    }

    return file_paths.get(file_path)


'''
=================================================================================
                            Redirect Inactive LP's
=================================================================================
'''


def redirect_lp():
    '''
    Allows user to add redirecting script to all landing pages belonging to completed campaigns
    '''
    # Gets redirect base URL
    redirect_link = naming[source_country]['id']['redirect']

    # Doublecheck if user is sure he wants to continue
    choice = ''
    while choice.lower() != 'y' and choice.lower() != 'n':
        print(f'\n{Fore.YELLOW}» {Fore.WHITE}Continue with redirecting '
              f'all WK{source_country} completed campaign LPs to:'
              f'\n  {Fore.YELLOW}{redirect_link}{Fore.WHITE}? ({YES}/{NO}):', end=' ')
        choice = input('')
        if choice.lower() == 'y':
            break
        elif choice.lower() == 'n':
            return False

    # Builds search query for campaign API
    search_query = f"name='WK{source_country}*'"

    # Iterates over pages of outcomes
    page = 1
    completed_campaigns = []
    print(f'{Fore.WHITE}[{Fore.YELLOW}SYNC{Fore.WHITE}] ', end='', flush=True)
    while True:
        campaigns = api.eloqua_get_campaigns(
            search_query, page=page, depth='minimal')

        # Creates list of completed campaigns » ['id', 'name']
        for campaign in campaigns['elements']:
            if campaign.get('currentStatus', 'Completed') == 'Completed':
                completed_campaigns.append(
                    [campaign.get('id'), campaign.get('name')]
                )

        # Stops iteration when full list is obtained
        if campaigns['total'] - page * 500 < 0:
            break

        # Else increments page to get next part of outcomes
        page += 1

        # Every ten batches draws hyphen for better readability
        if page % 10 == 0:
            print(f'{Fore.YELLOW}-', end='', flush=True)

    # TODO:
    # 3. Get all landing pages for those campaigns
    # 4. Modify all landing pages connected to those campaigns
    # 5. Mark that they are modified (either name or folder or description)

    return


'''
=================================================================================
                            Modifier module menu
=================================================================================
'''


def modifier_module(country):
    '''
    Lets user choose which modifier module utility he wants to use
    '''
    # Create global source_country and load json file with naming convention
    country_naming_setter(country)

    # Campaign type chooser
    print(
        f'\n{Fore.GREEN}ELQuent.modifier Utilites:'
        f'\n{Fore.WHITE}[{Fore.YELLOW}1{Fore.WHITE}]\t» [{Fore.YELLOW}Redirect{Fore.WHITE}] Adds redirect script to completed campaigns LPs'
        f'\n{Fore.WHITE}[{Fore.YELLOW}Q{Fore.WHITE}]\t» [{Fore.YELLOW}Quit to main menu{Fore.WHITE}]'
    )
    while True:
        print(f'{Fore.YELLOW}Enter number associated with chosen utility:', end='')
        choice = input(' ')
        if choice.lower() == 'q':
            break
        elif choice == '1':
            redirect_lp()
            break
        else:
            print(f'{Fore.RED}Entered value does not belong to any utility!')
            choice = ''

    return
