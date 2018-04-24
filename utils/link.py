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
        'elqtrack': find_data_file(f'{name}.txt'),
        'utmswap': find_data_file(f'{name}.txt')
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


def output_method(code, email_id, name):
    '''
    Allows user choose how the program should output the results
    '''

    print(
        f'\n{Fore.GREEN}New code should be:',
        f'\n{Fore.WHITE}[{Fore.YELLOW}0{Fore.WHITE}]\t{Fore.YELLOW}» {Fore.WHITE}Only saved to Outcomes folder',
        f'\n{Fore.WHITE}[{Fore.YELLOW}1{Fore.WHITE}]\t{Fore.YELLOW}» {Fore.WHITE}Copied to clipboard for pasting [CTRL+V]',
        f'\n{Fore.WHITE}[{Fore.YELLOW}2{Fore.WHITE}]\t{Fore.YELLOW}» {Fore.WHITE}Uploaded to Eloqua to original E-mail with new elqTrack',
        f'\n{Fore.WHITE}[{Fore.YELLOW}3{Fore.WHITE}]\t{Fore.YELLOW}» {Fore.WHITE}Uploaded to Eloqua as a new E-mail with new elqTrack')
    while True:
        print(f'{Fore.YELLOW}Enter number associated with chosen utility:', end='')
        choice = input(' ')
        if choice == '0':
            break
        elif choice == '1':
            pyperclip.copy(code)
            break
        elif choice == '2':
            api.eloqua_update_email(email_id, code)
            break
        elif choice == '3':
            print(
                f'\n{Fore.WHITE}[{Fore.YELLOW}Original E-mail{Fore.WHITE}] {name}',
                f'\n{Fore.YELLOW}» Write or paste new E-mail name:')
            name = api.eloqua_asset_name()
            api.eloqua_create_email(name, code)
            break
        else:
            print(f'{Fore.RED}Entered value does not belong to any utility!')
            choice = ''


'''
=================================================================================
                            Cleaning functions
=================================================================================
'''


def clean_elq_track(country):
    '''
    Returns code without elqTrack UTMs
    '''
    global source_country
    source_country = country

    # Gets required data points
    name_and_code, email_id = get_code()
    name, code = name_and_code

    # Checks if there is anything to clear
    elq_track = re.compile(r'(\?|&)elqTrack.*?(?=(#|"))', re.UNICODE)
    if elq_track.findall(code):
        print(
            f'\n{Fore.WHITE}[{Fore.GREEN}SUCCESS{Fore.WHITE}] Cleaned {len(elq_track.findall(code))} elqTracks and saved to Outcomes folder.')
        code = elq_track.sub('', code)
        with open(file('elqtrack', name=name), 'w', encoding='utf-8') as f:
            f.write(code)
        # Asks if user want another method of code usage
        output_method(code, email_id, name)
    else:
        print(f'\t{ERROR}elqTrack not found')

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


def swap_utm_track(country, code='', email_id='', name=''):
    '''
    Returns code with swapped tracking scripts in links
    '''
    global source_country
    source_country = country

    while True:
        # Gets Email code
        if not code:
            name_and_code, email_id = get_code()
            name, code = name_and_code

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
            f'{Fore.WHITE}» Write or paste new UTM tracking script and click [Enter]')
        new_utm = input(' ')
        if utm_track.findall(new_utm + '"'):
            break
        print(f'{ERROR}Entered UTM tracking script is incorrect')

    # Asks if phone field should be changed to lead mechanism
    swapping = ''
    while swapping.lower() != 'y' and swapping.lower() != 'n':
        print(f'\n{Fore.WHITE}Change UTM tracking script? (Y/N)',
              f'\n{Fore.WHITE}From › {Fore.YELLOW}{(utm_track.findall(code))[0][0]}',
              f'\n{Fore.WHITE}To › {Fore.YELLOW}{new_utm}')
        swapping = input(' ')

    if swapping.lower() == 'y':
        print(
            f'{Fore.GREEN}» Swapped {len(utm_track.findall(code))} UTM tracking scripts and saved to Outcomes folder.')
        code = utm_track.sub(new_utm, code)
        with open(file('utmswap', name=name), 'w', encoding='utf-8') as f:
            f.write(code)
        # Asks if user want another method of code usage
        output_method(code, email_id, name)

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
        swap_utm_track(country, code, email_id, name)

    return
