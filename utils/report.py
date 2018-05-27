#!/usr/bin/env python3.6
# -*- coding: utf8 -*-

'''
ELQuent.report
Reporting module using predefined Eloqua contact segments

Mateusz Dąbrowski
github.com/MateuszDabrowski
linkedin.com/in/mateusz-dabrowski-marketing/
'''

# Python imports
import os
import sys
import json
from datetime import date
from colorama import Fore, init

# ELQuent imports
import utils.api.api as api

# Globals
naming = None
source_country = None

# Initialize colorama
init(autoreset=True)

# Predefined messege elements
ERROR = f'{Fore.WHITE}[{Fore.RED}ERROR{Fore.WHITE}] {Fore.YELLOW}'
WARNING = f'{Fore.WHITE}[{Fore.YELLOW}WARNING{Fore.WHITE}] '
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


def file(file_path):
    '''
    Returns file path to template files
    '''

    def find_data_file(filename, directory):
        '''
        Returns correct file path for both script and frozen app
        '''
        if directory == 'api':  # For reading api files
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

    # Gets current date
    today = str(date.today().strftime('%d-%m-%y'))

    file_paths = {
        'naming': find_data_file('naming.json', directory='api'),
        'kpi': find_data_file(f'WK{source_country}_KPI_{today}.json', directory='outcomes')
    }

    return file_paths.get(file_path)


'''
=================================================================================
                                KPI Report Flow
=================================================================================
'''


def kpi_report(country):
    '''
    Outputs KPI report with predefined data
    '''

    # Create global source_country and load json file with naming convention
    country_naming_setter(country)

    # Shortcut for getting particular kpi segment id's
    kpi = naming[source_country]['kpi']

    def contact_count():
        '''
        Returns data about:
        - Eloqua contact count
        - Conctact count of particular marketing segments
        '''
        # Refresh segment to get up to date data
        api.eloqua_segment_refresh(kpi['contact_count'])

        # Gets data from segment
        segment_json = api.eloqua_asset_get(
            kpi['contact_count'],
            asset_type='Segment',
            depth='complete'
        )

        # Saves counts to appropriate variables
        for element in segment_json['elements']:
            if element['filter']['name'] == 'ALL':
                eloqua_contacts = int(element['filter']['count'])
            elif element['filter']['name'] == 'PRW':
                prw_contacts = int(element['filter']['count'])
            elif element['filter']['name'] == 'PUB':
                pub_contacts = int(element['filter']['count'])
            elif element['filter']['name'] == 'FIR':
                fir_contacts = int(element['filter']['count'])

        # Calculates others
        oth_contacts = eloqua_contacts - \
            (prw_contacts + pub_contacts + fir_contacts)

        return (eloqua_contacts, prw_contacts, pub_contacts, fir_contacts, oth_contacts)

    contact_counts = contact_count()
    print(contact_counts)

    return
