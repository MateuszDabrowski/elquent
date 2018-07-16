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
from datetime import datetime
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
                                Helper functions
=================================================================================
'''


def export_timeframe():
    '''
    Returns timeframe for export
    '''

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

    return (start_date, end_date)


'''
=================================================================================
                        Export Bounceback Activity Flow
=================================================================================
'''


def export_bouncebacks():
    '''
    Exports bouncebacks with Eloqua Bulk API
    Converts response to .csv and saves to outcomes
    '''

    # Gets payload for preparation
    with open(file('definition'), 'r', encoding='utf-8') as f:
        definition = f.read()

    start_date, end_date = export_timeframe()

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

    return


'''
=================================================================================
                            Export Campaign Data
=================================================================================
'''


def export_campaigns():
    '''
    Exports campaigns by country with Eloqua REST API
    Converts response to .csv and saves to outcomes
    '''

    # Gets timeframe for export and converts dates to unix
    start_date, end_date = export_timeframe()
    unix_start = int(datetime.strptime(start_date, '%m-%d-%Y').timestamp())
    unix_end = int(datetime.strptime(end_date, '%m-%d-%Y').timestamp())

    # Builds search query for API
    search_query = f"name='WK{source_country}*'createdAt>='{unix_start}'createdAt<='{unix_end}'"

    # Creates file to save outcomes
    with open(file('outcome-csv', f'campaigns-{start_date}-{end_date}'), 'w', encoding='utf-8') as f:
        fieldnames = ['Name', 'ID', 'Status', 'CreatedBy', 'CreatedAt', 'UpdatedAt',
                      'Start', 'End', 'Type', 'Folder']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

    # Iterates over pages of outcomes
    page = 1
    while True:
        campaigns = api.eloqua_get_campaigns(search_query, page)

        # Creates dict with data from API
        for campaign in campaigns['elements']:
            campaign_info = {
                'Name': campaign['name'],
                'ID': int(campaign['id']),
                'Status': campaign['currentStatus'],
                'CreatedBy': int(campaign['createdBy']),
                'CreatedAt': datetime.utcfromtimestamp(int(campaign['createdAt'])).strftime('%Y-%m-%d %H:%M:%S'),
                'UpdatedAt': datetime.utcfromtimestamp(int(campaign['updatedAt'])).strftime('%Y-%m-%d %H:%M:%S'),
                'Folder': int(campaign['folderId']),
                'Type': 'multistep' if campaign['isEmailMarketingCampaign'] == 'false' else 'simple'
            }

            # Getting start date and end date of campaign in a way that takes care of blanks
            try:
                campaign_info['Start'] = datetime.utcfromtimestamp(
                    int(campaign['startAt'])).strftime('%Y-%m-%d %H:%M:%S')
            except KeyError:
                campaign_info['Start'] = '0'
            try:
                campaign_info['End'] = datetime.utcfromtimestamp(
                    int(campaign['endAt'])).strftime('%Y-%m-%d %H:%M:%S')
            except KeyError:
                campaign_info['End'] = '0'

            # Append batch of data to file
            with open(file('outcome-csv', f'campaigns-{start_date}-{end_date}'), 'a', encoding='utf-8') as f:
                fieldnames = ['Name', 'ID', 'Status', 'CreatedBy', 'CreatedAt', 'UpdatedAt',
                              'Start', 'End', 'Type', 'Folder']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writerow(campaign_info)

        # Clears dict for next batch
        campaign_info = {}

        # Stops iteration when full list is obtained
        if campaigns['total'] - page * 40 < 0:
            break

        # Else increments page to get next part of outcomes
        page += 1

        # Every ten batches draws hyphen for better readability
        if page % 10 == 0:
            print(f'{Fore.YELLOW}-', end='', flush=True)

    print(f'\n{SUCCESS}Campaign export saved to Outcomes folder')

    return


'''
=================================================================================
                                Link module menu
=================================================================================
'''


def export_module(country):
    '''
    Lets user choose which export module utility he wants to use
    '''

    # Create global source_country and load json file with naming convention
    country_naming_setter(country)

    print(
        f'\n{Fore.GREEN}ELQuent.export Utilites:'
        f'\n{Fore.WHITE}[{Fore.YELLOW}1{Fore.WHITE}]\t» [{Fore.YELLOW}Bounceback{Fore.WHITE}] Export bouncebacks by bounce date'
        f'\n{Fore.WHITE}[{Fore.YELLOW}2{Fore.WHITE}]\t» [{Fore.YELLOW}Campaign{Fore.WHITE}] Export campaign data by creation date'
        f'\n{Fore.WHITE}[{Fore.YELLOW}Q{Fore.WHITE}]\t» [{Fore.YELLOW}Quit to main menu{Fore.WHITE}]'
    )
    while True:
        print(f'{Fore.YELLOW}Enter number associated with chosen utility:', end='')
        choice = input(' ')
        if choice.lower() == 'q':
            break
        elif choice == '1':
            export_bouncebacks()
            break
        elif choice == '2':
            export_campaigns()
            break
        else:
            print(f'{Fore.RED}Entered value does not belong to any utility!')
            choice = ''

    return
