#!/usr/bin/env python3.6
# -*- coding: utf8 -*-

'''
ELQuent.helper
Helper module storing functions for other modules

Mateusz Dąbrowski
github.com/MateuszDabrowski
linkedin.com/in/mateusz-dabrowski-marketing/
'''

# Python imports
import os
import sys
import json
from datetime import datetime
import pyperclip
from colorama import Fore, Style, init

# ELQuent imports
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
        elif directory == 'api':  # For reading api files
            if getattr(sys, 'frozen', False):
                datadir = os.path.dirname(sys.executable)
            else:
                datadir = os.path.dirname(os.path.dirname(__file__))
            return os.path.join(datadir, 'utils', directory, filename)

    file_paths = {
        'naming': find_data_file('naming.json', directory='api'),
        'outcome-json': find_data_file(f'WK{source_country}_{name}.json', directory='outcomes')
    }

    return file_paths.get(file_path)


'''
=================================================================================
                                Helper functions
=================================================================================
'''


def campaign_name_getter():
    '''
    Returns valid campaign name [list]
    '''
    while True:
        print(
            f'\n{Fore.WHITE}» [{Fore.YELLOW}CAMPAIGN{Fore.WHITE}]',
            f'{Fore.WHITE}Write or copypaste name of the Campaign and click [Enter]')
        campaign_name = input('')
        if not campaign_name:
            campaign_name = pyperclip.paste()
        campaign_name = campaign_name.split('_')

        # Structure check & vsp selector
        if len(campaign_name) == 5 and '/' not in '_'.join(campaign_name):
            print(f'\n{WARNING}This campaign name is build using old naming convention.',
                  f'\n{Fore.WHITE}» {Fore.RED}Are you sure you want to continue? '
                  f'{Fore.WHITE}({YES}/{NO}):', end=' ')
            name_decision = input('')
            if name_decision.lower() != 'y':
                continue
            vsp_element = campaign_name[4]
        elif len(campaign_name) == 6 and '/' in '_'.join(campaign_name):
            vsp_element = campaign_name[4].split('/')[0]
        else:
            print(f'{ERROR}Expected 6 name elements, found {len(campaign_name)}')
            continue

        # Get short part of campaign_name to differentiate type
        diff_name = '_'.join(
            [campaign_name[2], campaign_name[3].split('-')[0]])

        # Value check
        if campaign_name[0][:2] != 'WK':
            print(f'{ERROR}"{campaign_name[0]}" is not existing country code')
        elif campaign_name[1] not in naming[source_country]['segment']:
            print(f'{ERROR}"{campaign_name[1]}" is not existing segment name')
        elif campaign_name[2] not in naming['campaign']:
            print(f'{ERROR}"{campaign_name[2]}" is not existing campaign type')
        elif vsp_element not in naming['vsp']:
            print(f'{ERROR}"{campaign_name[4]}" is not existing VSP')
        elif diff_name.startswith('RET_LA') or (campaign_name[1] == 'MSG' and campaign_name[2] == 'NSL'):
            if diff_name in naming[source_country]['mail']['by_name'].keys():
                break
            else:
                print(f'{ERROR}"{diff_name}" is not correct campaign type')
        else:
            break

    return campaign_name


def date_swapper(date):
    '''
    Changes date format from DD-MM-YYYY to MM-DD-YYYY and the other way round
    '''
    date_parts = date.split('-')
    swapped_date = f'{date_parts[1]}-{date_parts[0]}-{date_parts[2]}'

    return swapped_date


def epoch_to_date(epoch):
    '''
    Converts epoch timestamp to readable date format DD-MM-YYYY
    '''
    if not epoch:
        return False
    else:
        readable_date = datetime.fromtimestamp(int(epoch))
        readable_date = readable_date.strftime('%d-%m-%Y')

        return readable_date


def epoch_to_time(epoch):
    '''
    Converts epoch timestamp to readable time format HH:MM
    '''
    if not epoch:
        return False
    else:
        readable_time = datetime.fromtimestamp(int(epoch))
        readable_time = readable_time.strftime('%H:%M')

        return readable_time


def date_to_epoch(date):
    '''
    Converts datetime timestamp to epoch format [integer]
    '''
    if not date:
        return False
    else:
        epoch = int(date.timestamp())

        return epoch


def epoch_getter():
    '''
    Gets date and time from user [DD-MM-YY hh-mm]
    Returns date and time in epoch form [integer]
    '''
    while True:
        # Gets datetime from user
        print(f'\n{Fore.WHITE}» [{Fore.YELLOW}WEBINAR{Fore.WHITE}] ',
              f'{Fore.WHITE}Enter webinar date (DD-MM-YYYY hh:mm) and click [Enter]')
        user_date = input(' ')
        # Tries to change it to epoch if valid
        try:
            webinar_date = datetime.strptime(user_date, '%d-%m-%Y %H:%M')
            webinar_epoch = date_to_epoch(webinar_date)
            break
        except ValueError:
            print(f'{ERROR}Incorrect date and time format!')

    return webinar_epoch


def user_getter(user_id):
    '''
    Returns data on Eloqua user with provided ID
    '''
    user = api.eloqua_get_user(user_id)

    user_dict = {
        'id': user['id'],
        'name': user['name'],
        # 'mail': user['emailAddress'],
        'createdAt': datetime.utcfromtimestamp(
            int(user['createdAt'])).strftime('%Y-%m-%d %H:%M:%S')
    }

    return user_dict


def asset_name_getter():
    '''
    Returns:
    - type of asset used in campaign (ebook/webinar/code) [string]
    - asset type (shorthand of converter choice) [string]
    - asset name [string]
    '''
    # Gets information about converter that is used in campaign
    print(f'\n{Fore.GREEN}After filling the form user receives:')
    converter_values = list(naming[source_country]['converter'].keys())
    for i, converter in enumerate(converter_values[1:]):
        print(
            f'{Fore.WHITE}[{Fore.YELLOW}{i}{Fore.WHITE}] {converter}')
    while True:
        print(f'{Fore.YELLOW}Enter number associated with your choice:', end='')
        converter_choice = input(' ')
        if converter_choice in ['0', '1', '2', '3', '4']:
            converter_choice = converter_values[int(converter_choice) + 1]
            asset_type = converter_choice.split(' ')[0]
            if converter_choice == 'Test Access':
                asset_name = ''
                break
            else:
                print(
                    f'\n{Fore.WHITE}» [{Fore.YELLOW}ASSET{Fore.WHITE}] Enter title of the {asset_type}')
                asset_name = input(' ')
                if not asset_name:
                    asset_name = pyperclip.paste()
                    if not asset_name:
                        print(f'\n{ERROR}Title can not be blank')
                        continue
                elif len(asset_name) > 200:
                    print(f'\n{ERROR}Title is over 200 characters long')
                    continue
                break
        else:
            print(f'{ERROR}Entered value does not belong to any choice!')

    return (converter_choice, asset_type, asset_name)


def asset_link_getter():
    '''
    Returns link to campaign asset [string]
    '''
    while True:
        print(
            f'\n{Fore.WHITE}» [{Fore.YELLOW}URL{Fore.WHITE}] Enter link to the asset or asset page')
        asset_url = input(' ')
        if not asset_url:
            asset_url = pyperclip.paste()
        if asset_url.startswith('http') or asset_url.startswith('www'):
            asset_url = asset_url.replace('http://images.go.wolterskluwer.com',
                                          'https://img06.en25.com')
            if '?' in asset_url:
                asset_url = asset_url + '&elqTrack=true'
            else:
                asset_url = asset_url + '?elqTrack=true'
            break
        else:
            print(f'{ERROR}Entered value is not valid link!')

    return asset_url


def external_page_getter():
    '''
    Returns link to external landing page and null id [touple of strings]
    '''
    while True:
        print(
            f'\n{Fore.WHITE}» [{Fore.YELLOW}URL{Fore.WHITE}] ',
            f'{Fore.WHITE}Enter link to the external landing page with the form')
        external_url = input(' ')
        if not external_url:
            external_url = pyperclip.paste()
        # Checks if input is a link
        if external_url.startswith('http') or external_url.startswith('www'):
            # Checks if there is utm already in the input
            if 'utm' in external_url or 'elqTrack' in external_url:
                print(f'{ERROR}Please enter link without tracking!')
                continue
            break
        else:
            print(f'{ERROR}Entered value is not valid link!')

    return (external_url, '')


def product_name_getter(campaign_name=''):
    '''
    Returns name of the product from campaign name or user input [string]
    '''
    # Gets product name either from campaign name or user
    local_name = campaign_name[3].split('-')
    if local_name[0] in naming[source_country]['product']:
        product_name = naming[source_country]['product'][local_name[0]]
    else:
        while True:
            print(
                f'\n{Fore.WHITE}» [{Fore.YELLOW}PRODUCT{Fore.WHITE}]',
                f'{Fore.WHITE}Could not recognize product name, please write its name: ', end='')
            product_name = input(' ')
            if not product_name:
                product_name = pyperclip.paste()
                if not product_name:
                    print(f'\n{ERROR}Product name can not be blank')
                    continue
            elif len(product_name) > 60:
                print(f'\n{ERROR}Product name is over 60 characters long')
                continue
            else:
                break

    return product_name


def header_text_getter():
    '''
    Returns optional text for header
    '''
    while True:
        print(f'\n{Fore.WHITE}» [{Fore.YELLOW}OPTIONAL{Fore.WHITE}]',
              f'{Fore.WHITE}Text to be displayed on the left side of header bar:')
        header_text = input(' ')
        if not header_text:
            header_text = pyperclip.paste()
        elif len(header_text) > 60:
            print(f'\n{ERROR}Optional text is over 60 characters long')
            continue
        else:
            break

    return header_text
