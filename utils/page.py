#!/usr/bin/env python3.6
# -*- coding: utf8 -*-

'''
ELQuent.page
RegEx Eloqua LP & Form automator

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


def file(file_path):
    '''
    Returns file path to template files
    '''
    def find_data_file(filename, dir='templates'):
        '''
        Returns correct file path for both script and frozen app
        '''
        if dir == 'templates':  # For reading template files
            if getattr(sys, 'frozen', False):
                datadir = os.path.dirname(sys.executable)
            else:
                datadir = os.path.dirname(os.path.dirname(__file__))
            return os.path.join(datadir, 'utils', dir, filename)
        elif dir == 'outcomes':  # For writing outcome files
            if getattr(sys, 'frozen', False):
                datadir = os.path.dirname(sys.executable)
            else:
                datadir = os.path.dirname(os.path.dirname(__file__))
            return os.path.join(datadir, dir, filename)

    file_paths = {
        'blank-lp': find_data_file('WKCORP_blank-lp.txt'),
        'one-column-lp': find_data_file(f'WK{source_country}_one-column-lp.txt'),
        'two-column-lp': find_data_file(f'WK{source_country}_two-column-lp.txt'),
        'showhide-css': find_data_file(f'WK{source_country}_showhide-css.txt'),
        'marketing-optin': find_data_file(f'WK{source_country}_marketing-optin.txt'),
        'email-optin': find_data_file(f'WK{source_country}_email-optin.txt'),
        'phone-optin': find_data_file(f'WK{source_country}_phone-optin.txt'),
        'tracking-optin': find_data_file(f'WK{source_country}_tracking-optin.txt'),
        'validation-body': find_data_file('WKCORP_validation-body.txt'),
        'validation-element': find_data_file(f'WK{source_country}_validation-element.txt'),
        'landing-page': find_data_file(f'WK{source_country}_LP.txt', dir='outcomes')
    }

    return file_paths.get(file_path)


'''
=================================================================================
                        Landing Page focused functions
=================================================================================
'''


def create_landing_page():
    '''
    Returns code of the Landing Page
    '''

    def get_code(choice):
        '''
        Returns Landing Page Code either form clipoard or from template
        '''

        def clean_custom_css(lp_code):
            '''
            Returns LP code without Custom Form CSS
            '''
            regex = re.compile(
                r'<!-- StartFormCustomCSS[\s\S]*?EndFormCustomCSS -->', re.UNICODE)
            if regex.findall(lp_code):
                print(f'\t{Fore.CYAN}» Cleaning Custom Form CSS')
            lp_code = re.sub(regex, '', lp_code)

            return lp_code

        def add_showhide_css(lp_code):
            '''
            Returns LP code with CSS ShowHide solution
            '''
            regex = re.compile(r'\.read-more-state', re.UNICODE)
            match = regex.findall(lp_code)
            if not match:
                print(f'\t{Fore.CYAN}» Adding ShowHide CSS')
                with open(file('showhide-css'), 'r', encoding='utf-8') as f:
                    css = f.read()
                regex = re.compile(r'</style>', re.UNICODE)
                lp_code = re.sub(regex, css, lp_code, 1)

            return lp_code

        print()
        if choice == (len(options) - 1):  # Gets code from clipboard
            input(
                f'{Fore.WHITE}» [{Fore.YELLOW}LP{Fore.WHITE}] Copy code of the Landing Page [CTRL+C] and click [Enter]')
            lp_code = pyperclip.paste()
            lp_code = clean_custom_css(lp_code)
            lp_code = add_showhide_css(lp_code)
        else:  # Gets code from template file
            templates = ['blank-lp', 'one-column-lp', 'two-column-lp']
            with open(file(templates[choice]), 'r') as f:
                lp_code = f.read()

        return lp_code

    options = [
        f'{Fore.WHITE}[{Fore.YELLOW}TEMPLATE{Fore.WHITE}] Create Blank Landing Page with Form',
        f'{Fore.WHITE}[{Fore.YELLOW}TEMPLATE{Fore.WHITE}] Create One Column Landing Page with Form',
        f'{Fore.WHITE}[{Fore.YELLOW}TEMPLATE{Fore.WHITE}] Create Two Column Landing Page with Form',
        f'{Fore.WHITE}[{Fore.YELLOW}EXISTING{Fore.WHITE}] Change form in existing Landing Page'
    ]

    print(f'\n{Fore.GREEN}You can:')
    for i, option in enumerate(options):
        print(f'{Fore.WHITE}[{Fore.YELLOW}{i}{Fore.WHITE}]\t{option}')
    print(
        f'{Fore.WHITE}[{Fore.YELLOW}R{Fore.WHITE}]\t{Fore.WHITE}Return to main menu',
        f'\n{Fore.WHITE}[{Fore.YELLOW}Q{Fore.WHITE}]\t{Fore.WHITE}Quit')

    while True:
        choice = input(
            f'{Fore.YELLOW}Enter number associated with your choice: ')
        if choice.lower() == 'r':
            return False
        if choice.lower() == 'q':
            print(f'\n{Fore.GREEN}Ahoj!')
            raise SystemExit
        try:
            choice = int(choice)
        except ValueError:
            print(f'{Fore.RED}Please enter numeric value!')
            continue
        if 0 <= choice < len(options):
            break
        else:
            print(f'{Fore.RED}Entered value does not belong to any utility!')

    return get_code(choice)


def swap_form(code, form):
    '''
    Returns LP code with new form
    '''
    regex_style = re.compile(
        r'<style type[\s\S]*?elq-form[\s\S]*?<\/style>', re.UNICODE)
    code = re.sub(regex_style, '', code)
    regex_form = re.compile(
        r'<div>\s*?<form method[\s\S]*?dom0[\s\S]*?<\/script>\s*?<\/div>', re.UNICODE)
    match = regex_form.findall(code)
    if match:
        code = re.sub(regex_form, form, code)
        print(f'\t{Fore.GREEN} » Swapping Form in Landing Page')
    elif len(match) == 0:
        regex_placeholder = re.compile(r'<INSERT_FORM>')
        is_placeholder = regex_placeholder.findall(code)
        if is_placeholder:
            code = re.sub(regex_placeholder, form, code)
            print(f'\t{Fore.GREEN} » Adding Form to Landing Page')
        else:
            print(
                f'{Fore.RED}» [Error] there is no form or placeholder in code.\n',
                f'{Fore.WHITE} (Add <INSERT_FORM> where you want the form and rerun program)')
    elif len(match) >= 1:
        print(f'{Fore.RED}[Error] there are {len(match)} forms in the code')

    return code


'''
=================================================================================
                           Eloqua Form focused functions
=================================================================================
'''


def get_form():
    '''
    Returns code of new Form
    '''
    input(
        f'{Fore.WHITE}» [{Fore.YELLOW}FORM{Fore.WHITE}] Copy code of the new Form [CTRL+C] and click [Enter]')
    return pyperclip.paste()


def optin_version(form, optin_path_names):
    '''
    Returns names of existing marketing, email, phone and tracking optins
    '''
    optins = {}

    # Iterates over possible HTML names of opt-in form fields to save existing optins
    for optin_type in optin_path_names.items():
        for optin_name in optin_type[1]:
            optin_search = re.compile(rf'name="{optin_name}"', re.UNICODE)
            optin_match = optin_search.findall(form)
            if optin_match:
                optins[f'{optin_type[0][0]}'] = f'{optin_name}'

    return optins


def swap_optins(form, optins, optin_path_names):
    '''
    Returns code of new Form with correct opt ins text
    '''
    requiredOptins = []

    # Creates dict of {(optin_type, optin_path): 'in_form_optin_name'}
    form_optins = {}
    for optin in optin_path_names.items():
        for name in optins.values():
            if name in optin[1]:
                form_optins[optin[0]] = name

    if len(form_optins) != len(optins):
        error = f'\n {Fore.RED} » Non standard HTML name of opt-in form field\n'
        raise ValueError(error)

    for optin in form_optins.items():
        # Loads opt-in new code
        with open(optin[0][1], 'r', encoding='utf-8') as file:
            optin_text = file.read()
        # Create regex to swap opt-in in form code
        regex_optin = re.compile(
            rf'<input name="{optin[1]}"[\s\S]*?<\/p>', re.UNICODE)

        # Swaps HTML name of opt-in to language correct
        regex_language = re.compile(r'<INSERT_OPTIN>', re.UNICODE)
        optin_text = re.sub(regex_language, rf'{optin[1]}', optin_text)

        # Asks if opt-in is required and apply choice
        required = ''
        while required.lower() != 'y' and required.lower() != 'n':
            print(
                f'\t{Fore.WHITE}Is {optin[0][0]} Opt-in ({optin[1]}) required? (Y/N):', end='')
            required = input(' ')
        if required.lower() == 'y':
            requiredOptins.append(optin[1])
            regex_req = re.compile(r'read-more-wrap">', re.UNICODE)
            optin_text = re.sub(
                regex_req, 'read-more-wrap"><span class="required">*</span> ', optin_text, 1)
        print(f'\t{Fore.CYAN} » Expanding {optin[0][0]} Opt-in ({optin[1]})')

        # Adds new opt-ins to form code
        form = re.sub(regex_optin, optin_text, form)

    form, requiredOptins = additional_required_checkboxes(
        form, optins, requiredOptins)

    return (form, requiredOptins)


def additional_required_checkboxes(form, optins, required):
    '''
    Returns full list of required checkboxes
    '''

    # Gets formElement ID, input name and input type
    regex_id_name = re.compile(
        r'formElement(.|..)"[\s\S]*?name="(.+?)"', re.UNICODE)
    id_name = regex_id_name.findall(form)

    # Gets input name and type
    regex_name_type = re.compile(r'name="(.*?)".*?type="(.*?)"', re.UNICODE)
    name_type = regex_name_type.findall(form)

    # Builds list of checkboxes with formElement ID and input name
    checkbox = [x for (x, y) in name_type if y == 'checkbox']
    checkbox = [(x, y) for (x, y) in id_name if y in checkbox]
    required_checkbox = [(x, y) for (x, y) in checkbox if y in required]
    unknown_checkbox = [(x, y)
                        for (x, y) in checkbox if y not in optins.values()]

    # Ask user which additional checkboxes are required
    for checkbox in unknown_checkbox:
        required = ''
        while required.lower() != 'y' and required.lower() != 'n' and required.lower() != '0':
            print(
                f'\t{Fore.WHITE}Is "{checkbox[1]}" checkbox required? (Y/N):', end='')
            required = input(' ')
        if required.lower() == 'y':
            required_checkbox += (checkbox,)
            regex_req = re.compile(
                rf'(formElement{checkbox[0]}[\s\S]*?checkbox-label...)(\n)', re.UNICODE)
            form = re.sub(
                regex_req, r'\1<span class="required">*</span> ', form, 1)
            print(f'\t{Fore.CYAN} » Adding {checkbox[1]} as required')
        elif required.lower() == 'n':
            print(f'\t{Fore.CYAN} » Setting {checkbox[1]} as not required')
        elif required == '0':
            print(f'\t{Fore.CYAN} » Setting all left checkboxes as not required')
            break

    return (form, required_checkbox)


'''
=================================================================================
                           Validation focused functions
=================================================================================
'''


def validation_js(code, required):
    '''
    Returns Landing Page code with proper checkbox js validation
    '''

    def del_validation_js(code):
        '''
        Returns LP code without JavaScript checkbox validation
        '''
        regex = re.compile(
            r'<script.*?\n\s*?\$\(document\)[\s\S]*?requiredChecked[\s\S]*?script>', re.UNICODE)
        if regex.findall(code):
            print(f'\t{Fore.CYAN} » Cleaning Checkbox Validation')
        code = re.sub(regex, '', code)

        return code

    def add_validation_js(code, required):
        '''
        Returns LP code with new JavaScript checkbox validation
        '''

        # Adds checkbox validation body to LP code
        with open(file('validation-body'), 'r', encoding='utf-8') as f:
            validation_body = f.read()
        regex_validation = re.compile(r'</body>', re.UNICODE)
        code = re.sub(regex_validation, validation_body, code)

        # Adds checkbox validation element to LP code
        regex_element_id = re.compile(r'INSERT_ID', re.UNICODE)
        regex_element_name = re.compile(r'INSERT_NAME', re.UNICODE)
        regex_element_insert = re.compile(r'//requiredChecked', re.UNICODE)
        for req in required:
            with open(file('validation-element'), 'r', encoding='utf-8') as f:
                validation_element = f.read()
            validation_element = re.sub(
                regex_element_id, req[0], validation_element)
            validation_element = re.sub(
                regex_element_name, req[1], validation_element)
            code = re.sub(regex_element_insert, validation_element, code)
        print(f'\t{Fore.GREEN} » Adding new Checkbox Validation')

        return code

    code = del_validation_js(code)
    code = add_validation_js(code, required)

    return code


'''
=================================================================================
                                Main program flow
=================================================================================
'''


def page_gen(country):
    '''
    Main menu for ELQuent.page module
    Returns new Landing page code
    '''
    # Create global source_country from main module
    global source_country
    source_country = country

    # Checks if there are required source files for the source source_country
    if not os.path.exists(file('validation-element')):
        input(
            f'\n{Fore.RED}[ERROR] No template found for WK{source_country}.\n{Fore.WHITE}[Enter] to continue.')
        return False

    # Collects possible HTML names of opt-in form fields
    optin_path_names = {
        ('Marketing', file('marketing-optin')): ('directMailOptedIn1', 'zgoda_marketingowa', 'privacy'),
        ('Email', file('email-optin')): ('emailOptedIn1', 'zgoda_handlowa', 'optin'),
        ('Phone', file('phone-optin')): ('phoneOptedIn1', 'zgoda_telefoniczna'),
        ('Tracking', file('tracking-optin')): ('Tracking',)
    }

    # Landing Page code manipulation
    code = create_landing_page()
    form = get_form()
    optins = optin_version(form, optin_path_names)
    form, required = swap_optins(form, optins, optin_path_names)
    code = swap_form(code, form)
    code = validation_js(code, required)

    # Two way return of new code
    pyperclip.copy(code)
    with open(file('landing-page'), 'w', encoding='utf-8') as f:
        f.write(code)
    print(
        f'\n{Fore.GREEN}» You can now paste new Landing Page to Eloqua [CTRL+V].',
        f'\n{Fore.WHITE}  (It is also saved as WK{source_country}_LP.txt in Outcomes folder)\n')
    input(f'{Fore.WHITE}» Click [Enter] to continue.')

    return True
