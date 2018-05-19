#!/usr/bin/env python3.6
# -*- coding: utf8 -*-

'''
ELQuent.dashboard
Eloqua Dashboard module for plotting information

Mateusz Dąbrowski
github.com/MateuszDabrowski
linkedin.com/in/mateusz-dabrowski-marketing/
'''

# Python imports
import os
import sys
import json
from colorama import Fore, init

# ELQuent imports
import utils.api.api as api

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

    def find_data_file(filename, directory):
        '''
        Returns correct file path for both script and frozen app
        '''
        if directory == 'api':  # For reading api files
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
        'forms': find_data_file(f'WK{source_country}_form-data.json', directory='outcomes'),

    }

    return file_paths.get(file_path)


'''
=================================================================================
                            Form Filling Report
=================================================================================
'''


def form_fill_report(country):
    '''
    Gets report data via ELQuent.api
    Outputs .csv with raw data
    Creates visualisation
    '''

    # Create global source_country and load json file with naming convention
    country_naming_setter(country)

    def get_form_fields():
        '''
        Returns list of form with name, id and fields (id, name, html name, type, requirement) in .json
        '''
        # Getting full form data from Eloqua
        forms_full_data = api.eloqua_get_forms()

        forms = []
        # Creates cleaned list of dicts with important data
        for form in forms_full_data:
            single_form = {}
            single_form['id'] = form['id']
            single_form['name'] = form['name']
            fields = []
            # Dives into list of form fields
            for element in form['elements']:
                field = {}
                field['field_name'] = element.get('name', None)
                field['id'] = element.get('id', None)
                field['field_html_name'] = element.get('htmlName', None)
                field['field_type'] = element.get('displayType', None)
                # Dives into list of validations - if they exist for form field
                if element.get('validations', False):
                    for validation in element['validations']:
                        if validation['condition'].get('type', None) == 'IsRequiredCondition' and validation.get('isEnabled', None) == 'true':
                            field['field_required'] = 'true'
                            break
                if not field.get('field_required', False):
                    field['field_required'] = 'false'
                fields.append(field)
            single_form['fields'] = fields
            forms.append(single_form)

        # Saves cleaned form list as json file to outcomes
        with open(file('forms'), 'w', encoding='utf-8') as f:
            json.dump(forms, f, ensure_ascii=False)
        print(
            f'  {SUCCESS}Data of {len(forms_full_data)} forms saved to Outcomes folder')

        return forms

    forms = get_form_fields()

    return
