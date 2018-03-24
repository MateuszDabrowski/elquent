#!/usr/bin/env python3.6
# -*- coding: utf8 -*-

'''
ELQuent.mail
RegEx cleaner of email HTML

Mateusz Dąbrowski
github.com/MateuszDabrowski
linkedin.com/in/mateusz-dabrowski-marketing/
'''

import re
import encodings
import pyperclip
from colorama import Fore, init

# Initialize colorama
init(autoreset=True)

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
    input(f'\n{Fore.WHITE}» Copy code of eMail [CTRL+C] and click [Enter]')
    return pyperclip.paste()


'''
=================================================================================
                            Cleaning functions
=================================================================================
'''


def clean_elqtrack():
    '''
    Returns eMails code without elqTrack UTMs
    » code: long str
    '''
    code = get_email_code()
    regex = re.compile(r'(?:\?|&)elqTrack.*?(?=")', re.UNICODE)
    occurance = len(regex.findall(code))
    if occurance:
        print(f'\t{Fore.YELLOW}» Cleaned {occurance} elqTrack instances')
        code = re.sub(regex, '', code)
        pyperclip.copy(code)
        print(f'{Fore.GREEN}» You can now paste eMail to Eloqua [CTRL+V].',)
    else:
        print(f'\t{Fore.RED}» elqTrack not found')
    input(f'{Fore.WHITE}Click [Enter] to continue.')
    return code
