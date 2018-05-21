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
        'outcome': find_data_file(f'WK{source_country}_{name}.csv', directory='outcomes')
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
    valid_date = re.compile(r'[0-3]\d-[0-1]\d-20d\d')

    # Get start date
    while True:
        print(
            f'{Fore.WHITE}[{Fore.YELLOW}START{Fore.WHITE}] Enter export start date [DD-MM-YYYY]', end='')
        start_date = input(' ')
        if valid_date.findall(start_date):
            break
        else:
            print(f'{ERROR}Invalid date format » should be DD-MM-YYYY')

    # Get end date
    while True:
        print(
            f'{Fore.WHITE}[{Fore.YELLOW}END{Fore.WHITE}] Enter export end date [DD-MM-YYYY]', end='')
        end_date = input(' ')
        if valid_date.findall(end_date):
            break
        else:
            print(f'{ERROR}Invalid date format » should be in DD-MM-YYYY format')

    definition = definition\
        .replace('WKSC', f'WK{source_country}')\
        .replace('START_DATE', start_date)\
        .replace('END_DATE', end_date)

    # Changes txt to json for API call
    definition_json = json.loads(definition)

    export_uri = api.eloqua_post_export(
        definition_json, export_type='activity')
    sync_uri = api.eloqua_post_sync(export_uri, return_uri=True)
    export_jsons = api.eloqua_sync_data(sync_uri)

    # Opens .csv to output data
    with open(file('outcome', f'bouncebacks-{start_date}-{end_date}'), 'a', encoding='utf-8') as csv_output:
        bouncebacks = csv.writer(csv_output)
        bouncebacks.writerow([
            'ActivityId',
            'ActivityType',
            'ActivityDate',
            'EmailAddress',
            'AssetType',
            'AssetName',
            'CampaignId',
            'ExternalId',
            'EmailRecipientId',
            'DeploymentId',
            'SmtpErrorCode',
            'SmtpStatusCode',
            'SmtpMessage',
            'SFDCContactID_CF',
            'EloquaContactID_CF',
            'SFDCAccountID_CF',
            'CRM_ContactID_CF',
            'CRM_AccountID_CF',
            'CRM_Secondary_Contact_ID_CF',
            'CRM_Tertiary_Contact_ID_CF',
            'EmailAddress_CF',
            'CLSlabel_CF',
            'SourceCountry_CF'
        ])

        for export in export_jsons:
            for element in export['items']:
                bouncebacks.writerow(element.values())

    print(f'\n{SUCCESS}Bounceback export saved to .csv in Outcomes folder')
