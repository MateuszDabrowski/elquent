#!/usr/bin/env python3.6
# -*- coding: utf8 -*-

'''
ELQuent.report
Creates reports via Eloqua API

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
from colorama import Fore, Style, init

# ELQuent imports
import utils.helper as helper
import utils.api.api as api

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
        'outcome-csv': find_data_file(f'Report_{name}.csv', directory='outcomes'),
    }

    return file_paths.get(file_path)


'''
=================================================================================
                                Helper functions
=================================================================================
'''


def report_timeframe():
    '''
    Returns timeframe for reporting scope
    '''

    # Check date input format
    valid_date = re.compile(r'[0-3]\d-[0-1]\d-20\d\d')

    # Get start date
    while True:
        print(
            f'\n{Fore.WHITE}[{Fore.YELLOW}START{Fore.WHITE}] Enter export start date [DD-MM-YYYY]:', end='')
        report_start_date = input(' ')
        if valid_date.findall(report_start_date):
            report_start_epoch = int(
                datetime.strptime(report_start_date, '%d-%m-%Y').timestamp()
            )
            break
        else:
            print(f'{ERROR}Date should be in DD-MM-YYYY format\n')

    # Get end date
    while True:
        print(
            f'{Fore.WHITE}[{Fore.YELLOW}END{Fore.WHITE}] Enter export end date [DD-MM-YYYY]:', end='')
        report_end_date = input(' ')
        if valid_date.findall(report_end_date):
            report_end_epoch = int(
                datetime.strptime(report_end_date, '%d-%m-%Y').timestamp()
            )
            break
        else:
            print(f'{ERROR}Date should be in DD-MM-YYYY format\n')

    return (report_start_epoch, report_end_epoch, report_start_date, report_end_date)


def report_nameframe():
    '''
    Returns nameframe for reporting scope
    '''
    print(
        f'\n{Fore.WHITE}[{Fore.YELLOW}NAME{Fore.WHITE}] Enter part of the e-mail name to report:', end='')
    report_asset_name = input(' ')

    return report_asset_name


def report_search_query():
    '''
    Returns search query for reporting
    '''
    while True:
        unix_start, unix_end, report_start_date, report_end_date = report_timeframe()
        nameframe = report_nameframe()

        # Builds search query for API
        search_query = f"name='*{nameframe}*'createdAt>='{unix_start}'createdAt<='{unix_end}'"

        # Counts results
        search_results = api.eloqua_get_assets(
            search_query, asset_type='email', count=1, depth='minimal')
        total_results = search_results['total']

        print(f'\n{Fore.WHITE}» Found {Fore.YELLOW}{total_results}{Fore.WHITE} e-mails.',
              f'{Fore.WHITE}Continue? ({YES}/{NO}):', end=' ')
        choice = input('')
        if choice.lower() == 'y':
            break
        else:
            continue

    return (search_query, nameframe, report_start_date, report_end_date)


'''
=================================================================================
                                    Full Report
=================================================================================
'''


def full_report():
    '''
    Crates report with links to full Eloqua report for each e-mail in chosen scope
    '''

    # Gets confirmed search query from user
    search_query, nameframe, report_start_date, report_end_date = report_search_query()

    # Creates file to save outcomes
    with open(file('outcome-csv', f'full-{nameframe}-{report_start_date}-{report_end_date}'), 'w', encoding='utf-8') as f:
        fieldnames = ['Name', 'ID', 'CreatedAt', 'Report']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

    # Gets instance url for link creation
    instance_url = naming['root'][:-10]

    page = 1
    print(f'{Fore.WHITE}[{Fore.YELLOW}SYNC{Fore.WHITE}] ', end='', flush=True)
    while True:
        emails = api.eloqua_get_assets(
            search_query, asset_type='email', page=page, depth='minimal')

        # Creates list with data from API
        for email in emails['elements']:
            email_info = {
                'Name': email['name'],
                'ID': int(email['id']),
                'CreatedAt': datetime.utcfromtimestamp(
                    int(email['createdAt'])).strftime('%Y-%m-%d %H:%M:%S'),
                'Report': f'{instance_url}/Analytics/Dashboard/EmailDetail?EmailId={email["id"]}'
            }

            # Append batch of data to file
            with open(file('outcome-csv', f'full-{nameframe}-{report_start_date}-{report_end_date}'), 'a', encoding='utf-8') as f:
                fieldnames = ['Name', 'ID', 'CreatedAt', 'Report']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writerow(email_info)

        # Clears dict for next batch
        email_info = {}

        # Stops iteration when full list is obtained
        if emails['total'] - page * 500 < 0:
            break

    print(f'\n\n{SUCCESS}E-mail Report for {Fore.YELLOW}{nameframe} {Fore.WHITE}({Fore.YELLOW}{report_start_date}'
          f'{Fore.WHITE} - {Fore.YELLOW}{report_end_date}{Fore.WHITE}) saved to Outcomes folder')

    return


'''
=================================================================================
                                Report module menu
=================================================================================
'''


def report_module(country):
    '''
    Lets user choose which report module utility he wants to use
    '''

    # Create global source_country and load json file with naming convention
    country_naming_setter(country)

    # Report type chooser
    print(
        f'\n{Fore.GREEN}ELQuent.report Utilites:'
        f'\n{Fore.WHITE}[{Fore.YELLOW}1{Fore.WHITE}]\t» [{Fore.YELLOW}Full{Fore.WHITE}] Exports full report URLs for e-mails'
        f'\n{Fore.WHITE}[{Fore.YELLOW}Q{Fore.WHITE}]\t» [{Fore.YELLOW}Quit to main menu{Fore.WHITE}]'
    )
    while True:
        print(f'{Fore.YELLOW}Enter number associated with chosen utility:', end='')
        choice = input(' ')
        if choice.lower() == 'q':
            break
        elif choice == '1':
            full_report()
            break
        else:
            print(f'{Fore.RED}Entered value does not belong to any utility!')
            choice = ''

    return
