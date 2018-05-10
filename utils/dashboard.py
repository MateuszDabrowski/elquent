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
import webbrowser
from colorama import Fore, init

# Dash imports
import dash
import dash_core_components as core
import dash_html_components as html

# ELQuent imports
import utils.api.api as api

# Initialize colorama
init(autoreset=True)

# Globals
app = dash.Dash()
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

    def find_data_file(filename):
        '''
        Returns correct file path for both script and frozen app
        '''
        if getattr(sys, 'frozen', False):
            datadir = os.path.dirname(sys.executable)
        else:
            datadir = os.path.dirname(os.path.dirname(__file__))
        return os.path.join(datadir, 'utils', 'api', filename)

    file_paths = {
        'naming': find_data_file('naming.json'),
        'click': find_data_file('click.p')
    }

    return file_paths.get(file_path)


'''
=================================================================================
                            Form Filling Report
=================================================================================
'''


def form_fill_dash(country):
    '''
    Prepares and launches form field fill report
    '''

    country_naming_setter(country)

    app.layout = html.Div(
        style={'fontFamily': ('Fira Sans', 'Arial')},
        children=[
            html.H1(children='ELQuent.dashboard'),
            html.P(children='Work in progress.',
                   style={'fontSize': '36'}),

            core.Graph(
                id='form-graph',
                figure={
                    'data': [
                        {'x': [1, 2, 3], 'y': [4, 1, 2],
                         'type': 'bar', 'name': 'Orange'},
                        {'x': [1, 2, 3], 'y': [2, 4, 5],
                         'type': 'bar', 'name': 'Blue'},
                    ],
                    'layout': {
                        'title': 'Test graph for dashboard'
                    }
                }
            )
        ])

    print(f'\n{SUCCESS}Opening form filling dashboard',
          f'\n{Fore.YELLOW}Press [CTRL]+[C] to return to main menu\n')
    app_url = 'http://127.0.0.1:8050'
    webbrowser.open(app_url, new=2, autoraise=False)
    app.run_server()
