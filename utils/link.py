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
import pyperclip
from colorama import Fore, Style, init

# ELQuent imports
import utils.api.api as api

# Initialize colorama
init(autoreset=True)

# Globals
source_country = None

# Predefined messege elements
ERROR = f'{Fore.WHITE}[{Fore.RED}ERROR{Fore.WHITE}] {Fore.YELLOW}'
SUCCESS = f'{Fore.WHITE}[{Fore.GREEN}SUCCESS{Fore.WHITE}] '
YES_NO = f'{Fore.WHITE}({Style.BRIGHT}{Fore.GREEN}y{Fore.WHITE}{Style.NORMAL}\
          /{Style.BRIGHT}{Fore.RED}n{Fore.WHITE}{Style.NORMAL})'


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
    if email_id:
        try:
            email = api.eloqua_asset_get(email_id, asset_type='Mail')
        except KeyError:
            print(f'  {ERROR}Cannot clean drag & drop e-mail')
    else:
        while True:
            print(
                f'\n{Fore.WHITE}» [{Fore.YELLOW}CODE{Fore.WHITE}] Copy code [CTRL+C] and click [Enter]', end='')
            input(' ')
            code = pyperclip.paste()
            is_html = re.compile(r'<html[\s\S\n]*?</html>', re.UNICODE)
            if is_html.findall(code):
                print(
                    f'{Fore.WHITE}» [{Fore.YELLOW}NAME{Fore.WHITE}] Write or paste new E-mail name:')
                name = api.eloqua_asset_name()
                email = (name, code)
                break
            print(f'  {ERROR}Copied code is not correct HTML')

    return email, email_id


def output_method(code, email_id, name):
    '''
    Allows user choose how the program should output the results
    '''
    print(
        f'\n{Fore.GREEN}New code should be:',
        f'\n{Fore.WHITE}[{Fore.YELLOW}0{Fore.WHITE}]\t»',
        f'{Fore.WHITE}[{Fore.YELLOW}FILE{Fore.WHITE}] Only saved to Outcomes folder',
        f'\n{Fore.WHITE}[{Fore.YELLOW}1{Fore.WHITE}]\t»',
        f'{Fore.WHITE}[{Fore.YELLOW}COPY{Fore.WHITE}] Copied to clipboard for pasting [CTRL+V]',
        f'\n{Fore.WHITE}[{Fore.YELLOW}2{Fore.WHITE}]\t»',
        f'{Fore.WHITE}[{Fore.YELLOW}CREATE{Fore.WHITE}] Uploaded to Eloqua as a new E-mail with new elqTrack')
    if email_id:
        print(
            f'{Fore.WHITE}[{Fore.YELLOW}3{Fore.WHITE}]\t»',
            f'{Fore.WHITE}[{Fore.YELLOW}UPDATE{Fore.WHITE}] Uploaded to Eloqua to original E-mail with new elqTrack')
    while True:
        print(f'{Fore.YELLOW}Enter number associated with chosen utility:', end='')
        choice = input(' ')
        if choice == '0':
            break
        elif choice == '1':
            pyperclip.copy(code)
            print(
                f'\n{Fore.WHITE}[{Fore.YELLOW}HTML{Fore.WHITE}]{Fore.GREEN} You can now paste [CTRL+V]')
            break
        elif choice == '2':
            print(
                f'\n{Fore.WHITE}[{Fore.YELLOW}Original E-mail{Fore.WHITE}] {name}',
                f'\n{Fore.WHITE}» [{Fore.YELLOW}NAME{Fore.WHITE}] Write or paste new E-mail name:')
            name = api.eloqua_asset_name()
            api.eloqua_create_email(name, code)
            break
        elif choice == '3' and email_id:
            api.eloqua_update_email(email_id, code)
            break
        else:
            print(f'{Fore.RED}Entered value does not belong to any utility!')
            choice = ''


'''
=================================================================================
                                Cleaning functions
=================================================================================
'''


def clean_elq_track():
    '''
    Returns code without elqTrack UTMs
    '''

    # Gets required data points
    name_and_code, email_id = get_code()
    name, code = name_and_code

    # Checks if there is anything to clear
    elq_track = re.compile(r'((\?|&)elqTrack.*?(?=(#|")))', re.UNICODE)
    if elq_track.findall(code):
        print(
            f'\n{Fore.WHITE}[{Fore.GREEN}SUCCESS{Fore.WHITE}]',
            f'{Fore.WHITE}Cleaned {len(elq_track.findall(code))} elqTracks and saved to Outcomes folder.')
        code = elq_track.sub('', code)
        with open(file('elqtrack', name=name), 'w', encoding='utf-8') as f:
            f.write(code)
        # Asks if user want another method of code usage
        output_method(code, email_id, name)
    else:
        print(f'\t{ERROR}elqTrack not found')

    # Asks user if he would like to repeat
    print(f'\n{Fore.WHITE}» Do you want to clean another code? {YES_NO}:', end=' ')
    choice = input(' ')
    if choice.lower() == 'y':
        print(
            f'\n{Fore.GREEN}-----------------------------------------------------------------------------')
        clean_elq_track()

    return


'''
=================================================================================
                                Swapping functions
=================================================================================
'''


def swap_utm_track(code='', email_id='', name=''):
    '''
    Returns code with swapped tracking scripts in links
    '''

    while True:
        # Gets Email code
        if not code:
            name_and_code, email_id = get_code()
            name, code = name_and_code

        # Cleans ELQ tracking
        elq_track = re.compile(r'((\?|&)elqTrack.*?(?=(#|")))', re.UNICODE)
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
        print(f'\n{Fore.WHITE}Change UTM tracking script?',
              f'\n{Fore.WHITE}From › {Fore.YELLOW}{(utm_track.findall(code))[0][0]}',
              f'\n{Fore.WHITE}To › {Fore.YELLOW}{new_utm}',
              f'\n{YES_NO}:', end=' ')
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
    print(
        f'\n{Fore.WHITE}» Do you want to swap another UTM tracking?',
        f'\n{Fore.WHITE}({Style.BRIGHT}{Fore.GREEN}y{Fore.WHITE}/{Fore.RED}n{Fore.WHITE}/{Fore.YELLOW}a{Style.NORMAL}{Fore.WHITE}nother',
        f'{Fore.WHITE}UTM change in the same code)', end='')
    choice = input(' ')
    if choice.lower() == 'y':
        print(
            f'\n{Fore.GREEN}-----------------------------------------------------------------------------')
        swap_utm_track()
    elif choice.lower() == 'a':
        print(
            f'\n{Fore.GREEN}-----------------------------------------------------------------------------', end='\n')
        swap_utm_track(code, email_id, name)

    return


'''
=================================================================================
                                Link module menu
=================================================================================
'''


def link_module(country):
    '''
    Lets user choose which link module utility he wants to use
    '''
    global source_country
    source_country = country

    print(
        f'\n{Fore.GREEN}ELQuent.link Utilites:'
        f'\n{Fore.WHITE}[{Fore.YELLOW}1{Fore.WHITE}]\t» [{Fore.YELLOW}ELQ{Fore.WHITE}] Delete elqTrack code in E-mail links'
        f'\n{Fore.WHITE}[{Fore.YELLOW}2{Fore.WHITE}]\t» [{Fore.YELLOW}UTM{Fore.WHITE}] Swap UTM tracking code in E-mail links'
        f'\n{Fore.WHITE}[{Fore.YELLOW}Q{Fore.WHITE}]\t» [{Fore.YELLOW}Quit to main menu{Fore.WHITE}]'
    )
    while True:
        print(f'{Fore.YELLOW}Enter number associated with chosen utility:', end='')
        choice = input(' ')
        if choice.lower() == 'q':
            break
        elif choice == '1':
            clean_elq_track()
            break
        elif choice == '2':
            swap_utm_track()
            break
        else:
            print(f'{Fore.RED}Entered value does not belong to any utility!')
            choice = ''
