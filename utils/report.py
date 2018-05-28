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
import datascience as ds
import matplotlib.pyplot as plots

# ELQuent imports
import utils.api.api as api

# Globals
naming = None
source_country = None

# Plots style
plots.style.use('fivethirtyeight')

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

    def segment_array_for(category):
        '''
        Returns array of results for given KPI category
        '''

        # Refresh segment to get up to date data
        api.eloqua_segment_refresh(kpi[category])

        # Gets data from segment
        segment_json = api.eloqua_asset_get(
            kpi[category],
            asset_type='Segment',
            depth='complete'
        )

        # Saves counts to appropriate variables
        for element in segment_json['elements']:
            if element['filter']['name'] == 'ALL+WMR':
                eloqua_and_wmr_contacts = int(element['filter']['count'])
            elif element['filter']['name'] == 'LEG+WMR':
                leg_and_wmr_contacts = int(element['filter']['count'])
            elif element['filter']['name'] == 'PUB+WMR':
                pub_and_wmr_contacts = int(element['filter']['count'])
            elif element['filter']['name'] == 'FIR+WMR':
                fir_and_wmr_contacts = int(element['filter']['count'])
            elif element['filter']['name'] == 'ALL-WMR':
                eloqua_sans_wmr_contacts = int(element['filter']['count'])
            elif element['filter']['name'] == 'LEG-WMR':
                leg_sans_wmr_contacts = int(element['filter']['count'])
            elif element['filter']['name'] == 'PUB-WMR':
                pub_sans_wmr_contacts = int(element['filter']['count'])
            elif element['filter']['name'] == 'FIR-WMR':
                fir_sans_wmr_contacts = int(element['filter']['count'])

        # Calculates others
        oth_and_wmr_contacts = eloqua_and_wmr_contacts - \
            (leg_and_wmr_contacts + pub_and_wmr_contacts + fir_and_wmr_contacts)
        oth_sans_wmr_contacts = eloqua_sans_wmr_contacts - \
            (leg_sans_wmr_contacts + pub_sans_wmr_contacts + fir_sans_wmr_contacts)

        print(f'{SUCCESS}Import finished for {category}')

        return ds.make_array(
            eloqua_and_wmr_contacts, eloqua_sans_wmr_contacts,
            leg_and_wmr_contacts, leg_sans_wmr_contacts,
            pub_and_wmr_contacts, pub_sans_wmr_contacts,
            fir_and_wmr_contacts, fir_sans_wmr_contacts,
            oth_and_wmr_contacts, oth_sans_wmr_contacts
        )

    # Creating table for KPI data
    print(f'\n{Fore.YELLOW}» {Fore.WHITE}Importing data from Eloqua')
    kpi_table = ds.Table().with_column(
        'Segment',
        ds.make_array(
            'ALL + WMR', 'ALL - WMR',
            'LEG + WMR', 'LEG - WMR',
            'PUB + WMR', 'PUB - WMR',
            'FIR + WMR', 'FIR - WMR',
            'OTH + WMR', 'OTH - WMR'
        )
    )

    # Getting data for particular columns
    contact_count = segment_array_for('contact_count')
    newsletter_count = segment_array_for('newsletter_count')
    newsletter_profinfo_count = segment_array_for('newsletter_profinfo_count')
    alert_count = segment_array_for('alert_count')
    sent_count = segment_array_for('sent_count')
    open_count = segment_array_for('open_count')
    click_count = segment_array_for('click_count')
    form_count = segment_array_for('form_count')
    not_opened_count = segment_array_for('not_opened_count')
    cookie_count = segment_array_for('cookie_count')

    # Adding data columns to KPI table
    kpi_table = kpi_table.with_columns(
        'Contacts', contact_count,
        'NSL', newsletter_count,
        'NSL Prof', newsletter_profinfo_count,
        'Alert', alert_count,
        'Sent (M)', sent_count,
        'Open (M)', open_count,
        'Click (M)', click_count,
        'Form (M)', form_count,
        # TODO: 'Unsub (M)', » form data API
        'Not Opened 10+ (Y)', not_opened_count,
        'Cookie Linked (A)', cookie_count
    )

    today = str(date.today().strftime('%d-%m-%y'))
    kpi_table.to_csv(f'WK{source_country}_KPI_{today}.csv')

    print(
        f'\n{SUCCESS}Report prepared and saved to ELQuent folder!',
        f'\n{Fore.WHITE}» Click [Enter] to continue.', end='')
    input(' ')

    return
