#!/usr/bin/env python3.6
# -*- coding: utf8 -*-

'''
ELQuent.export
Exports data via Eloqua Bulk API

Mateusz Dąbrowski
github.com/MateuszDabrowski
linkedin.com/in/mateusz-dabrowski-marketing/
'''

# Python imports
import os
import re
import sys
import csv
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
        elif directory == 'templates':  # For reading template files
            if getattr(sys, 'frozen', False):
                datadir = os.path.dirname(sys.executable)
            else:
                datadir = os.path.dirname(os.path.dirname(__file__))
            return os.path.join(datadir, 'utils', directory, filename)

    file_paths = {
        'naming': find_data_file('naming.json', directory='api'),
        'click': find_data_file('click.p', directory='api'),
        'definition': find_data_file(f'WK{source_country}_bounceback_export.txt', directory='templates'),
        'outcome-json': find_data_file(f'WK{source_country}_{name}.json', directory='outcomes'),
        'outcome-csv': find_data_file(f'WK{source_country}_{name}.csv', directory='outcomes')
    }

    return file_paths.get(file_path)


'''
=================================================================================
                        Export Bounceback Activity Flow
=================================================================================
'''


def export_bouncebacks(country):
    '''
    Exports bouncebacks with Eloqua Bulk API
    Converts response to .csv and saves to outcomes
    '''

    # Create global source_country and load json file with naming convention
    country_naming_setter(country)

    # Gets payload for preparation
    with open(file('definition'), 'r', encoding='utf-8') as f:
        definition = f.read()

    # Check date input format
    valid_date = re.compile(r'[0-1]\d-[0-3]\d-20\d\d')

    # Get start date
    while True:
        print(
            f'\n{Fore.WHITE}[{Fore.YELLOW}START{Fore.WHITE}] Enter export start date [MM-DD-YYYY] ', end='')
        start_date = input(' ')
        if valid_date.findall(start_date):
            break
        else:
            print(f'{ERROR}Date should be in MM-DD-YYYY format\n')

    # Get end date
    while True:
        print(
            f'{Fore.WHITE}[{Fore.YELLOW}END{Fore.WHITE}] Enter export end date [MM-DD-YYYY]', end='')
        end_date = input(' ')
        if valid_date.findall(end_date):
            break
        else:
            print(f'{ERROR}Date should be in MM-DD-YYYY format\n')

    definition = definition\
        .replace('WKSOURCECOUNTRY', f'WK{source_country}')\
        .replace('START_DATE', start_date)\
        .replace('END_DATE', end_date)

    # Changes txt to json for API call
    definition_json = json.loads(definition)

    # Bounceback activity export flow
    export_uri = api.eloqua_post_export(
        definition_json, export_type='activity')
    print(f'{Fore.WHITE}[{Fore.YELLOW}SYNC{Fore.WHITE}] ', end='', flush=True)
    sync_uri = api.eloqua_post_sync(export_uri, return_uri=True)
    export_json = api.eloqua_sync_data(sync_uri)

    if not export_json:
        print(f'\n{Fore.WHITE}» {ERROR}No bouncebacks found between {start_date} and {end_date} for WK{source_country}')
        return False

    # Saves export data to .json
    with open(file('outcome-json', f'bouncebacks-{start_date}-{end_date}'), 'w', encoding='utf-8') as f:
        json.dump(export_json, f)
    # Saves export data to .csv
    with open(file('outcome-csv', f'bouncebacks-{start_date}-{end_date}'), 'a', encoding='utf-8') as csv_output:
        bouncebacks = csv.writer(csv_output)
        headers = False
        for element in export_json:
            if not headers:
                bouncebacks.writerow(element.keys())
                headers = True
            bouncebacks.writerow(element.values())

    print(f'\n{SUCCESS}Bounceback export saved to Outcomes folder')

    return True
