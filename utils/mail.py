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
    print(
        f'\n{Fore.WHITE}» Copy code of eMail [CTRL+C] and click [Enter]', end='')
    input(' ')
    return pyperclip.paste()


'''
=================================================================================
                            Cleaning functions
=================================================================================
'''


def clean_elqtrack(country):
    '''
    Returns eMails code without elqTrack UTMs
    » code: long str
    '''
    global source_country
    source_country = country

    code = get_email_code()
    regex = re.compile(r'(?:\?|&)elqTrack.*?(?=")', re.UNICODE)
    occurance = len(regex.findall(code))
    if occurance:
        print(f'\t{Fore.YELLOW}» Cleaned {occurance} elqTrack instances')
        code = re.sub(regex, '', code)
        pyperclip.copy(code)
        with open(file(), 'w', encoding='utf-8') as f:
            f.write(code)
        print(
            f'\n{Fore.GREEN}» You can now paste eMail to Eloqua [CTRL+V].',
            f'\n{Fore.WHITE}  (It is also saved as WK{source_country}_EML.txt in Outcomes folder)',
            f'\n{Fore.WHITE}» Click [Enter] to continue.', end='')
        input(' ')
        return True
    else:
        print(f'\t{Fore.RED}» elqTrack not found',
              f'\n{Fore.WHITE}» Click [Enter] to continue.', end='')
        input(' ')
        return False
