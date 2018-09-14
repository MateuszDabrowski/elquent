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
import pyperclip
from colorama import Fore, init

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


def file(file_path):
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

    file_paths = {
        'naming': find_data_file('naming.json', directory='api'),
    }

    return file_paths.get(file_path)


'''
=================================================================================
                                Helper functions
=================================================================================
'''


def campaign_name_getter():
    '''
    Returns valid campaign name [string]
    '''
    while True:
        print(
            f'\n{Fore.WHITE}» [{Fore.YELLOW}CAMPAIGN{Fore.WHITE}]',
            f'{Fore.WHITE}Write or copypaste name of the Campaign and click [Enter]')
        campaign_name = input('')
        if not campaign_name:
            campaign_name = pyperclip.paste()
        campaign_name = campaign_name.split('_')
        if len(campaign_name) != 5:
            print(f'{ERROR}Expected 5 name elements, found {len(campaign_name)}')
        elif campaign_name[0][:2] != 'WK':
            print(f'{ERROR}"{campaign_name[0]}" is not existing country code')
        elif campaign_name[1] not in naming[source_country]['segment']:
            print(f'{ERROR}"{campaign_name[1]}" is not existing segment name')
        elif campaign_name[2] not in naming['campaign']:
            print(f'{ERROR}"{campaign_name[2]}" is not existing campaign type')
        elif campaign_name[4] not in naming['vsp']:
            print(f'{ERROR}"{campaign_name[4]}" is not existing VSP')
        else:
            break

    return campaign_name


def campaign_type_getter():
    '''
    Returns type of campaign (lead/contact/both) [int]
    '''
    print(f'\n{Fore.GREEN}After filling the form user is:',
          f'\n{Fore.WHITE}[{Fore.YELLOW}0{Fore.WHITE}] Either lead or not (depending on submission)',
          f'\n{Fore.WHITE}[{Fore.YELLOW}1{Fore.WHITE}] Always lead',
          f'\n{Fore.WHITE}[{Fore.YELLOW}2{Fore.WHITE}] Never lead')
    while True:
        print(f'{Fore.YELLOW}Enter number associated with your choice:', end=' ')
        lead_or_contact_form = input('')
        if lead_or_contact_form in ['0', '1', '2']:
            lead_or_contact_form = int(lead_or_contact_form)
            break
        else:
            print(f'{ERROR}Entered value does not belong to any choice!')

    return lead_or_contact_form


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
    for i, converter in enumerate(converter_values[2:]):
        print(
            f'{Fore.WHITE}[{Fore.YELLOW}{i}{Fore.WHITE}] {converter}')
    while True:
        print(f'{Fore.YELLOW}Enter number associated with your choice:', end='')
        converter_choice = input(' ')
        if converter_choice in ['0', '1', '2', '3', '4', '5']:
            converter_choice = converter_values[int(converter_choice) + 2]
            asset_type = converter_choice.split(' ')[0]
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
