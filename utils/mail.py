#!/usr/bin/env python3.6
# -*- coding: utf8 -*-

'''
ELQuent.mail
RegEx cleaner of email HTML

Mateusz Dąbrowski
github.com/MateuszDabrowski
linkedin.com/in/mateusz-dabrowski-marketing/
'''

import os
import re
import sys
import encodings
import pyperclip
from colorama import Fore, init

# Initialize colorama
init(autoreset=True)


def file():
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

    file_path = find_data_file(f'WK{source_country}_EML.txt')

    return file_path


'''
=================================================================================
                            Preparation of the program
=================================================================================
'''


def get_email_code():
    '''
    Returns eMail code to be cleaned
    » code: long str
    '''
    while True:
        print(
            f'\n{Fore.WHITE}» Copy code of eMail [CTRL+C] and click [Enter]', end='')
        input(' ')
        code = pyperclip.paste()
        is_html = re.compile(r'<html[\s\S\n]*?</html>', re.UNICODE)
        if is_html.findall(code):
            break
        print(f'\t{Fore.RED}[ERROR] {Fore.YELLOW}Copied code is not Email')

    return code


'''
=================================================================================
                            Cleaning functions
=================================================================================
'''


def clean_elq_track(country):
    '''
    Returns Email code without elqTrack UTMs
    » code: long str
    '''
    global source_country
    source_country = country

    code = get_email_code()
    elq_track = re.compile(r'(\?|&)elqTrack.*?(?=(#|"))', re.UNICODE)
    if elq_track.findall(code):
        print(
            f'\t{Fore.YELLOW}» Cleaned {len(elq_track.findall(code))} elqTrack instances')
        code = elq_track.sub('', code)
        pyperclip.copy(code)
        with open(file(), 'w', encoding='utf-8') as f:
            f.write(code)
        print(
            f'\n{Fore.GREEN}» You can now paste Email to Eloqua [CTRL+V].',
            f'\n{Fore.WHITE}  (It is also saved as WK{source_country}_EML.txt in Outcomes folder)')
    else:
        print(f'\t{Fore.RED}[ERROR] {Fore.YELLOW}elqTrack not found')
    
    # Asks user if he would like to repeat
    print(f'\n{Fore.GREEN}Do you want to clean another Email? (Y/N)', end='')
    choice = input(' ')
    if choice.lower() == 'y':
        clean_elq_track(country)
    else:
        return True


'''
=================================================================================
                            Swapping functions
=================================================================================
'''


def swap_utm_track(country):
    '''
    Returns Email code with swapped tracking scripts in links
    » code: long str
    '''
    global source_country
    source_country = country

    # Gets Email code
    code = get_email_code()

    # Cleans ELQ tracking
    elq_track = re.compile(r'(\?|&)elqTrack.*?(?=(#|"))', re.UNICODE)
    if elq_track.findall(code):
        code = elq_track.sub('', code)

    # Gets new UTM tracking
    utm_track = re.compile(r'((\?|&)(kampania|utm).*?)(?=(#|"))', re.UNICODE)
    while True:
        print(
            f'{Fore.WHITE}» Copy new UTM tracking script [CTRL+C] and click [Enter]', end='')
        input(' ')
        new_utm = pyperclip.paste()
        if utm_track.findall(new_utm + '"'):
            break
        print(
            f'\t{Fore.RED}[ERROR] {Fore.YELLOW}Copied code is not correct UTM tracking script')

    # Asks if phone field should be changed to lead mechanism
    swapping = ''
    while swapping.lower() != 'y' and swapping.lower() != 'n':
        print(f'\n{Fore.WHITE}Change UTM tracking script from:',
              f'\n{Fore.WHITE}"{Fore.CYAN}{(utm_track.findall(code))[0][0]}{Fore.WHITE}"',
              f'\n{Fore.WHITE}to:',
              f'\n{Fore.WHITE}"{Fore.CYAN}{new_utm}{Fore.WHITE}"',
              f'\n{Fore.WHITE}? (Y/N)', end='')
        swapping = input(' ')

    if swapping.lower() == 'y':
        print(
            f'\t{Fore.YELLOW}» Swapped {len(utm_track.findall(code))} UTM tracking scripts')
        code = utm_track.sub(new_utm, code)
        pyperclip.copy(code)
        with open(file(), 'w', encoding='utf-8') as f:
            f.write(code)
        print(
            f'\n{Fore.GREEN}» You can now paste Email to Eloqua [CTRL+V].',
            f'\n{Fore.WHITE}  (It is also saved as WK{source_country}_EML.txt in Outcomes folder)')
    
    # Asks user if he would like to repeat
    print(f'\n{Fore.GREEN}Do you want to swap another UTM tracking? (Y/N)', end='')
    choice = input(' ')
    if choice.lower() == 'y':
        swap_utm_track(country)
    else:
        return True
