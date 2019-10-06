#!/usr/bin/env python3.6
# -*- coding: utf8 -*-

'''
ELQuent.minifier
E-mail code minifier

Mateusz Dąbrowski
github.com/MateuszDabrowski
linkedin.com/in/mateusz-dabrowski-marketing/
'''

import os
import re
import sys
import json
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


def file(file_path, file_name=''):
    '''
    Returns file path to template files
    '''

    def find_data_file(filename, directory='outcomes'):
        '''
        Returns correct file path for both script and frozen app
        '''
        if directory == 'main':  # Files in main directory
            if getattr(sys, 'frozen', False):
                datadir = os.path.dirname(sys.executable)
            else:
                datadir = os.path.dirname(os.path.dirname(__file__))
            return os.path.join(datadir, filename)
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
        'mail_html': find_data_file(f'WK{source_country}_{file_name}.txt')
    }

    return file_paths.get(file_path)


'''
=================================================================================
                                Code Output Helper
=================================================================================
'''


def output_method(html_code):
    '''
    Allows user choose how the program should output the results
    Returns email_id if creation/update in Eloqua was selected
    '''
    # Asks which output
    print(
        f'\n{Fore.GREEN}New code should be:',
        f'\n{Fore.WHITE}[{Fore.YELLOW}0{Fore.WHITE}]\t»',
        f'{Fore.WHITE}[{Fore.YELLOW}FILE{Fore.WHITE}] Only saved to Outcomes folder',
        f'\n{Fore.WHITE}[{Fore.YELLOW}1{Fore.WHITE}]\t»',
        f'{Fore.WHITE}[{Fore.YELLOW}HTML{Fore.WHITE}] Copied to clipboard as HTML for pasting [CTRL+V]',
        f'\n{Fore.WHITE}[{Fore.YELLOW}2{Fore.WHITE}]\t»',
        f'{Fore.WHITE}[{Fore.YELLOW}CREATE{Fore.WHITE}] Uploaded to Eloqua as a new E-mail',
        f'\n{Fore.WHITE}[{Fore.YELLOW}3{Fore.WHITE}]\t»',
        f'{Fore.WHITE}[{Fore.YELLOW}UPDATE{Fore.WHITE}] Uploaded to Eloqua as update to existing E-mail')
    email_id = ''
    while True:
        print(f'{Fore.YELLOW}Enter number associated with chosen utility:', end='')
        choice = input(' ')
        if choice == '0':
            break
        elif choice == '1' and html_code:
            pyperclip.copy(html_code)
            print(
                f'\n{SUCCESS}You can now paste the HTML code [CTRL+V]')
            break
        elif choice == '2':
            print(
                f'\n{Fore.WHITE}[{Fore.YELLOW}NAME{Fore.WHITE}] » Write or copypaste name of the E-mail:')
            name = api.eloqua_asset_name()
            api.eloqua_create_email(name, html_code)
            break
        elif choice == '3':
            print(
                f'\n{Fore.WHITE}[{Fore.YELLOW}ID{Fore.WHITE}] » Write or copypaste ID of the E-mail to update:')
            email_id = input(' ')
            if not email_id:
                email_id = pyperclip.paste()
            api.eloqua_update_email(email_id, html_code)
            break
        else:
            print(f'{ERROR}Entered value does not belong to any utility!')
            choice = ''

        return


'''
=================================================================================
                                E-mail Minifier
=================================================================================
'''


def email_minifier(code):
    '''
    Requires html code of an e-mail
    Returns minified html code of an e-mail
    '''

    # HTML Minifier
    html_attr = ['html', 'head', 'style', 'body',
                 'table', 'tbody', 'tr', 'td', 'th', 'div']
    for attr in html_attr:
        code = re.sub(rf'{attr}>\s*\n\s*', f'{attr}>', code)
        code = re.sub(rf'\s*\n\s+<{attr}', f'<{attr}', code)
    code = re.sub(r'"\n+\s*', '" ', code)
    for attr in ['alt', 'title', 'data-class']:
        code = re.sub(rf'{attr}=""', '', code)
    code = re.sub(r'" />', '"/>', code)
    code = re.sub(r'<!--[^\[\]]*?-->', '', code)
    for attr in html_attr:
        code = re.sub(rf'{attr}>\s*\n\s*', f'{attr}>', code)
        code = re.sub(rf'\s*\n\s+<{attr}', f'<{attr}', code)

    # Conditional Comment Minifier
    code = re.sub(
        r'\s*\n*\s*<!--\[if mso \| IE\]>\s*\n\s*', '\n<!--[if mso | IE]>', code)
    code = re.sub(
        r'\s*\n\s*<!\[endif\]-->\s*\n\s*', '<![endif]-->\n', code)

    # CSS Minifier
    code = re.sub(r'{\s*\n\s*', '{', code)
    code = re.sub(r';\s*\n\s*}\n\s*', '} ', code)
    code = re.sub(r';\s*\n\s*', '; ', code)
    code = re.sub(r'}\n+', '} ', code)

    # Whitespace Minifier
    code = re.sub(r'\t', '', code)
    code = re.sub(r'\n+', ' ', code)
    while '  ' in code:
        code = re.sub(r' {2,}', ' ', code)

    # Trim lines to maximum of 500 characters
    count = 0
    newline_indexes = []
    for i, letter in enumerate(code):
        if count > 450:
            if letter in ['>', ' ']:
                newline_indexes.append(i)
                count = 0
        else:
            count += 1

    for index in reversed(newline_indexes):
        output = code[:index+1] + '\n' + code[index+1:]
        code = output

    # Takes care of lengthy links that extends line over 500 characters
    while True:
        lengthy_lines_list = re.findall(r'^.{500,}$', code, re.MULTILINE)
        if not lengthy_lines_list:
            break

        lengthy_link_regex = re.compile(r'href=\".{40,}?\"|src=\".{40,}?\"')
        for line in lengthy_lines_list:
            lengthy_link_list = re.findall(lengthy_link_regex, line)
            code = code.replace(
                lengthy_link_list[0], f'\n{lengthy_link_list[0]}')

    return code


def email_workflow(email_code=''):
    '''
    Minifies the e-mail code
    '''

    if email_code:
        module = True
    # Gets e-mail code if not delivered via argument
    elif not email_code:
        module = False
        print(
            f'\n{Fore.WHITE}[{Fore.YELLOW}Code{Fore.WHITE}] » Copy code of the E-mail to minify and click [Enter]:')
        input()
        email_code = pyperclip.paste()

        # Gets the code from the user
        while True:
            email_code = pyperclip.paste()
            is_html = re.compile(r'<html[\s\S\n]*?</html>', re.UNICODE)
            if is_html.findall(email_code):
                print(f'{Fore.WHITE}» {SUCCESS}Code copied from clipboard')
                break
            print(
                f'{Fore.WHITE}» {ERROR}Invalid HTML. Copy valid code and click [Enter]', end='')
            input(' ')

    # Saves original code to outcomes folder
    with open(file('mail_html', file_name='original_code'), 'w', encoding='utf-8') as f:
        f.write(email_code)

    # Gets file size of original file
    original_size = os.path.getsize(
        file('mail_html', file_name='original_code'))

    # Minified the code
    minified_code = email_minifier(email_code)

    # Saves minified code to outcomes folder
    with open(file('mail_html', file_name='minified_code'), 'w', encoding='utf-8') as f:
        f.write(minified_code)

    # Gets file size of minified file
    minified_size = os.path.getsize(
        file('mail_html', file_name='minified_code'))

    print(f'\n{Fore.WHITE}» {SUCCESS}E-mail was minified from {Fore.YELLOW}{round(original_size/1024)}kB'
          f'{Fore.WHITE} to {Fore.YELLOW}{round(minified_size/1024)}kB'
          f' {Fore.WHITE}({Fore.GREEN}-{round((original_size-minified_size)/original_size*100)}%{Fore.WHITE})!')

    if not module:
        # Outputs the code
        output_method(minified_code)

        # Asks user if he would like to repeat
        print(f'\n{Fore.YELLOW}» {Fore.WHITE}Do you want to {Fore.YELLOW}minify another Email{Fore.WHITE}?',
              f'{Fore.WHITE}({YES}/{NO}):', end=' ')
        choice = input('')
        if choice.lower() == 'y':
            print(
                f'\n{Fore.GREEN}-----------------------------------------------------------------------------')
            email_workflow()

    return


'''
=================================================================================
                                Minifier module menu
=================================================================================
'''


def minifier_module(country):
    '''
    Lets user minify the HTML code
    '''

    # Create global source_country and load json file with naming convention
    country_naming_setter(country)

    # Report type chooser
    print(
        f'\n{Fore.GREEN}ELQuent.minifier Utilites:'
        f'\n{Fore.WHITE}[{Fore.YELLOW}1{Fore.WHITE}]\t» [{Fore.YELLOW}E-mail{Fore.WHITE}] Minifies e-mail code'
        f'\n{Fore.WHITE}[{Fore.YELLOW}Q{Fore.WHITE}]\t» [{Fore.YELLOW}Quit to main menu{Fore.WHITE}]'
    )
    while True:
        print(f'{Fore.YELLOW}Enter number associated with chosen utility:', end='')
        choice = input(' ')
        if choice.lower() == 'q':
            break
        elif choice == '1':
            email_workflow()
            break
        else:
            print(f'{Fore.RED}Entered value does not belong to any utility!')
            choice = ''

    return
