#!/usr/bin/env python3.6
# -*- coding: utf8 -*-

'''
ELQuent.link
RegEx cleaner for links

Mateusz Dąbrowski
github.com/MateuszDabrowski
linkedin.com/in/mateusz-dabrowski-marketing/
'''

# Python imports
import os
import re
import sys
import encodings
import pyperclip
from colorama import Fore, init

# ELQuent imports
import utils.api.api as api

# Initialize colorama
init(autoreset=True)

# Predefined messege elements
ERROR = f'{Fore.RED}[ERROR] {Fore.YELLOW}'

'''
=================================================================================
                            File Path Getter
=================================================================================
'''


def file(file_path, name=''):
    '''
    Returns file path to template files
    '''

    def find_data_file(filename):
        '''
        Returns correct file path for both script and frozen app
        '''
        if getattr(sys, 'frozen', False):
            datadir = os.path.dirname(sys.executable)
        else:
            datadir = os.path.dirname(os.path.dirname(__file__))
        return os.path.join(datadir, 'outcomes', filename)

    if not name:
        name = f'WK{source_country}_SwappedUTM-Code.txt'

    file_paths = {
        'elqtrack': find_data_file(f'{name}.html'),
        'utmswap': find_data_file(f'{name}.html')
    }

    return file_paths.get(file_path)


'''
=================================================================================
                            Preparation of the program
=================================================================================
'''


def get_code():
    '''
    Returns code to be cleaned
    » code: long str
    '''
    email_id = api.get_asset_id('Mail')
    email = api.eloqua_get_email(email_id)

    return email, email_id


'''
=================================================================================
                            Cleaning functions
=================================================================================
'''


def clean_elq_track(country):
    '''
    Returns code without elqTrack UTMs
    » code: long str
    '''
    global source_country
    source_country = country

    name_and_code, email_id = get_code()
    name, code = name_and_code

    elq_track = re.compile(r'(\?|&)elqTrack.*?(?=(#|"))', re.UNICODE)
    if elq_track.findall(code):
        print(
            f'\n{Fore.WHITE}[{Fore.GREEN}SUCCESS{Fore.WHITE}] Cleaned {len(elq_track.findall(code))} elqTracks and saved to Outcomes folder.')
        code = elq_track.sub('', code)
        with open(file('elqtrack', name=name), 'w', encoding='utf-8') as f:
            f.write(code)
    else:
        print(f'\t{ERROR}elqTrack not found')

    # Asks if it should be uploaded to Eloqua
    print(
        f'\n{Fore.WHITE}» Update e-mail with newly tracked code in Eloqua? (Y/N)', end='')
    choice = input(' ')
    if choice.lower() == 'y':
        api.eloqua_update_email(email_id, code)

    # Asks user if he would like to repeat
    print(f'\n{Fore.WHITE}» Do you want to clean another code? (Y/N)', end='')
    choice = input(' ')
    if choice.lower() == 'y':
        print(
            f'\n{Fore.GREEN}-----------------------------------------------------------------------------')
        clean_elq_track(country)

    return


'''
=================================================================================
                            Swapping functions
=================================================================================
'''


def swap_utm_track(country, code='', name=''):
    '''
    Returns code with swapped tracking scripts in links
    » code: long str
    '''
    global source_country
    source_country = country

    while True:
        # Gets Email code
        if not code:
            name, code = get_code()

        # Cleans ELQ tracking
        elq_track = re.compile(r'(\?|&)elqTrack.*?(?=(#|"))', re.UNICODE)
        if elq_track.findall(code):
            code = elq_track.sub('', code)

        # Gets new UTM tracking
        utm_track = re.compile(
            r'((\?|&)(kampania|utm).*?)(?=(#|"))', re.UNICODE)
        if utm_track.findall(code):
            break
        else:
            print(f'{ERROR}Chosen e-mail does not have any UTM tracking script')
            code = ''

    while True:
        print(
            f'{Fore.WHITE}» Write or copy new UTM tracking script and click [Enter]')
        new_utm = input(' ')
        if utm_track.findall(new_utm + '"'):
            break
        print(f'{ERROR}It is not correct UTM tracking script')

    # Asks if phone field should be changed to lead mechanism
    swapping = ''
    while swapping.lower() != 'y' and swapping.lower() != 'n':
        print(f'\n{Fore.WHITE}Change UTM tracking script from:',
              f'\n{Fore.WHITE}› "{Fore.YELLOW}{(utm_track.findall(code))[0][0]}{Fore.WHITE}"',
              f'\n{Fore.WHITE}to:',
              f'\n{Fore.WHITE}› "{Fore.YELLOW}{new_utm}{Fore.WHITE}"',
              f'\n{Fore.WHITE}? (Y/N)', end='')
        swapping = input(' ')

    if swapping.lower() == 'y':
        print(
            f'{Fore.GREEN}» Swapped {len(utm_track.findall(code))} UTM tracking scripts')
        code = utm_track.sub(new_utm, code)
        pyperclip.copy(code)
        with open(file('utmswap', name=name), 'w', encoding='utf-8') as f:
            f.write(code)
        print(
            f'\n{Fore.GREEN}» You can now paste code to Eloqua [CTRL+V].',
            f'\n{Fore.WHITE}  (It is also saved as WK{source_country}_SwappedUTM-Code.txt in Outcomes folder)')

    # Asks user if he would like to repeat
    print(f'\n{Fore.WHITE}» Do you want to swap another UTM tracking?\n(Y/N or S for another UTM change in the same code)', end='')
    choice = input(' ')
    if choice.lower() == 'y':
        print(
            f'\n{Fore.GREEN}-----------------------------------------------------------------------------')
        swap_utm_track(country)
    elif choice.lower() == 's':
        print(
            f'\n{Fore.GREEN}-----------------------------------------------------------------------------', end='\n')
        swap_utm_track(country, code)

    return
