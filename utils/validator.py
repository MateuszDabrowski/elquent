#!/usr/bin/env python3.6
# -*- coding: utf8 -*-

'''
ELQuent.validator
ELQuent campaign and asset validator

Mateusz Dąbrowski
github.com/MateuszDabrowski
linkedin.com/in/mateusz-dabrowski-marketing/
'''

# Python imports
import os
import sys
import csv
import json
import webbrowser
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
        'outcome-csv': find_data_file(f'WK{source_country}_{name}.csv', directory='outcomes')
    }

    return file_paths.get(file_path)


'''
=================================================================================
                            Campaign Lifespan Program
=================================================================================
'''


def lifespan_analytics_menu(today):
    '''
    Automatically points at campaigns that require attention and allows to take action
    '''
    # Lists of attention needing campaigns
    over_10_prof = []
    over_90 = []
    over_365 = []

    # Builds lists with data from campaign-lifespan function
    with open(file('outcome-csv', f'active-campaigns-{today}'), 'r', encoding='utf-8') as f:
        export_reader = csv.reader(f)
        next(f)  # Skips header row
        # Each row is campaign data ['Name', 'ID', 'CreatedBy', 'CreatedAt', 'UpdatedAt', 'StartAt', 'EndAt', 'Members']
        for row in export_reader:
            delta = datetime.strptime(row[6], '%Y-%m-%d')\
                - datetime.strptime(row[5], '%Y-%m-%d')
            if 'WKPL_PROF_BOO' in row[0] and delta.days > 10:
                over_10_prof.append([row[1], row[0], row[2], delta.days])
            if delta.days > 90:
                over_90.append([row[1], row[0], row[2], delta.days])
            if delta.days > 365:
                over_365.append([row[1], row[0], row[2], delta.days])

    # Exits module if nothing requires attention
    if not over_10_prof and not over_90 and not over_365:
        print(f'{SUCCESS}No campaign end date requiring attention')
        return

    # Sorts lists by campaign lifespan
    over_10_prof = sorted(over_10_prof, key=lambda item: item[3], reverse=True)
    over_90 = sorted(over_90, key=lambda item: item[3], reverse=True)
    over_365 = sorted(over_365, key=lambda item: item[3], reverse=True)

    # Shows user outcome of analysis and allows him to dive deeper
    while True:
        print(f'\n{Fore.GREEN}Show:')
        # Analysis menu
        if over_10_prof and source_country == 'PL':
            print(
                f'{Fore.WHITE}[{Fore.YELLOW}0{Fore.WHITE}]\t» {Fore.YELLOW}{len(over_10_prof)} '
                f'{Fore.WHITE}Profinfo campaigns set for longer than {Fore.YELLOW}10{Fore.WHITE} days')
        if over_90:
            print(
                f'{Fore.WHITE}[{Fore.YELLOW}1{Fore.WHITE}]\t» {Fore.YELLOW}{len(over_90)} '
                f'{Fore.WHITE}campaigns set for longer than {Fore.YELLOW}90{Fore.WHITE} days')
        if over_365:
            print(
                f'{Fore.WHITE}[{Fore.YELLOW}2{Fore.WHITE}]\t» {Fore.YELLOW}{len(over_365)} '
                f'{Fore.WHITE}campaigns set for longer than {Fore.YELLOW}365{Fore.WHITE} days')
        print(
            f'{Fore.WHITE}[{Fore.YELLOW}Q{Fore.WHITE}]\t» [{Fore.YELLOW}Quit to main menu{Fore.WHITE}]')

        print(
            f'{Fore.GREEN}Enter number associated with chosen option:', end='')
        choice = input(' ')
        if choice.lower() == 'q':
            break
        elif choice == '0':
            print(f'\n{Fore.YELLOW}Profinfo Campaigns spanning over 10 days:')
            lifespan_analytics(over_10_prof)
        elif choice == '1':
            print(f'\n{Fore.YELLOW}Campaigns spanning over 90 days:')
            lifespan_analytics(over_90)
        elif choice == '2':
            print(f'\n{Fore.YELLOW}Campaigns spanning over a year:')
            lifespan_analytics(over_365)
        else:
            print(f'{Fore.RED}Entered value does not belong to any option!')
            choice = ''

    return


def lifespan_analytics(campaign_list):
    '''
    Shows chosen list of attention needing campaigns and allows to open them in Eloqua for further analysis
    campaign_list is a list of lists with ['id', 'name', 'createdBy', 'lifespan']
    '''
    for campaign in campaign_list:
        print(
            f'\n{Fore.YELLOW}» {Fore.WHITE}{campaign[1]}'
            f'\n{Fore.WHITE}[Span: {Fore.YELLOW}{campaign[3]} days{Fore.WHITE}] '
            f'{Fore.WHITE}[ID: {Fore.YELLOW}{campaign[0]}{Fore.WHITE}] '
            f'{Fore.WHITE}[User: {Fore.YELLOW}{campaign[2]}{Fore.WHITE}]')

    print(f'\n{Fore.YELLOW}» Open all those campaigns in Eloqua? '
          f'{Fore.WHITE}({YES}/{NO}):', end='')
    choice = input(' ')
    if choice.lower() == 'y':
        for campaign in campaign_list:
            # Open in new tab
            url = naming['root'] + '#campaigns&id=' + campaign[0]
            webbrowser.open(url, new=2, autoraise=True)

    return


def campaign_lifespan():
    '''
    Creates report containg all active campaigns with end date after chosen period
    '''
    # Creates list to store all active multistep campaigns
    active_campaigns = []

    '''
    =================================================== Gets IDs of all active multistep campaigns
    '''

    # Builds search query for API
    search_query = f"name='WK{source_country}*'"

    # Iterates over pages of outcomes
    page = 1
    print(f'\n{Fore.WHITE}[{Fore.YELLOW}SYNC{Fore.WHITE}] ',
          end='', flush=True)
    while True:
        campaigns = api.eloqua_get_campaigns(
            search_query, page, depth='minimal')

        # Adds active campaigns to a list
        for campaign in campaigns['elements']:
            if campaign['currentStatus'] == 'Active' and campaign['isEmailMarketingCampaign'] == 'false':
                active_campaigns.append(int(campaign['id']))

        # Stops iteration when full list is obtained
        if campaigns['total'] - page * 500 < 0:
            break

        # Else increments page to get next part of outcomes
        page += 1

        # Every ten batches draws hyphen for better readability
        if page % 10 == 0:
            print(f'{Fore.YELLOW}-', end='', flush=True)
    print(f'\n{SUCCESS}Exported all {len(active_campaigns)} active multistep campaigns for WK{source_country}')

    '''
    =================================================== Exports data of each active multistep campaign
    '''

    # Gets date for file naming
    today = str(datetime.now())[:10]

    # Dict of users for id to name swap
    user_dict = {}

    # Creates file to save outcomes
    with open(file('outcome-csv', f'active-campaigns-{today}'), 'w', encoding='utf-8') as f:
        fieldnames = ['Name', 'ID', 'CreatedBy', 'CreatedAt', 'UpdatedAt',
                      'StartAt', 'EndAt', 'Members']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

    # Gets data on each active multistep campaign
    print(f'\n{Fore.WHITE}[{Fore.YELLOW}SYNC{Fore.WHITE}] ',
          end='', flush=True)
    for campaign_id in active_campaigns:
        campaign = api.eloqua_get_campaign(campaign_id)

        campaign_info = {
            'Name': campaign['name'],
            'ID': int(campaign['id']),
            'CreatedAt': datetime.utcfromtimestamp(int(campaign['createdAt'])).strftime('%Y-%m-%d %H:%M:%S'),
            'UpdatedAt': datetime.utcfromtimestamp(int(campaign['updatedAt'])).strftime('%Y-%m-%d %H:%M:%S'),
            'StartAt': datetime.utcfromtimestamp(int(campaign['startAt'])).strftime('%Y-%m-%d'),
            'EndAt': datetime.utcfromtimestamp(int(campaign['endAt'])).strftime('%Y-%m-%d'),
        }

        # Gets user name with least API calls required
        try:
            campaign_info['CreatedBy'] = user_dict[campaign['createdBy']]
        except KeyError:
            user_dict[campaign['createdBy']] = helper.user_getter(
                campaign['createdBy']).get('name', campaign['createdBy'])
            campaign_info['CreatedBy'] = user_dict[campaign['createdBy']]

        # Gets member count for the campain if any
        try:
            campaign_info['Members'] = campaign['memberCount']
        except KeyError:
            campaign_info['Members'] = '0'

        # Append batch of data to file
        with open(file('outcome-csv', f'active-campaigns-{today}'), 'a', encoding='utf-8') as f:
            fieldnames = ['Name', 'ID', 'CreatedBy', 'CreatedAt', 'UpdatedAt',
                          'StartAt', 'EndAt', 'Members']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writerow(campaign_info)

        # Clears dict for next batch
        campaign_info = {}

        print(f'{Fore.GREEN}|', end='', flush=True)
    print(
        f'\n{SUCCESS}Saved data of {len(active_campaigns)} campaigns to Outcomes folder')

    lifespan_analytics_menu(today)

    return


'''
=================================================================================
                                Validator module menu
=================================================================================
'''


def validator_module(country):
    '''
    Lets user choose which link module utility he wants to use
    '''
    # Create global source_country and load json file with naming convention
    country_naming_setter(country)

    # Campaign type chooser
    print(
        f'\n{Fore.GREEN}ELQuent.validator Utilites:'
        f'\n{Fore.WHITE}[{Fore.YELLOW}1{Fore.WHITE}]\t» [{Fore.YELLOW}Lifespan{Fore.WHITE}] Exports time data of all active multistep campaigns'
        f'\n{Fore.WHITE}[{Fore.YELLOW}Q{Fore.WHITE}]\t» [{Fore.YELLOW}Quit to main menu{Fore.WHITE}]'
    )
    while True:
        print(f'{Fore.YELLOW}Enter number associated with chosen utility:', end='')
        choice = input(' ')
        if choice.lower() == 'q':
            break
        elif choice == '1':
            campaign_lifespan()
            break
        else:
            print(f'{Fore.RED}Entered value does not belong to any utility!')
            choice = ''

    return
