#!/usr/bin/env python3.6
# -*- coding: utf8 -*-

'''
ELQuent.api
Basic api functions for other modules

Mateusz Dąbrowski
github.com/MateuszDabrowski
linkedin.com/in/mateusz-dabrowski-marketing/
'''

import os
import sys
import base64
import pickle
import getpass
import requests
import encodings
import pyperclip
from colorama import Fore, init

# Initialize colorama
init(autoreset=True)

# If you want to print API connection status codes, set debug to True
DEBUG = False


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
        return os.path.join(datadir, 'api', filename)

    file_paths = {
        'eloqua': find_data_file('eloqua.p'),
        'click': find_data_file('click.p')
    }

    return file_paths.get(file_path)


'''
=================================================================================
                                Main API functions
=================================================================================
'''


def status_code(response, root):
    '''
    Arguments:
        reponse - response from api_request function
        root - root URL of API call
    Returns boolean of API connection.
    '''

    if (response.status_code >= 200) and (response.status_code < 400):
        print(f'{Fore.YELLOW}» {root} '
              f'{Fore.GREEN}({response.status_code})')
        connected = True
    elif response.status_code >= 400:
        print(f'{Fore.YELLOW}» {root} '
              f'{Fore.RED}({response.status_code})')
        connected = False
    else:
        print(f'{Fore.YELLOW}» {root} '
              f'{Fore.BLUE}({response.status_code})')
        connected = False

    return connected


def api_request(root, eloqua_auth, call='get', api='eloqua', status=DEBUG, data={}):
    '''
    Arguments:
        root - root URL of API call
        call - either GET or POST
        api - either elouqa or click
    Returns response from Eloqua API call.
    '''

    # Assings correct authorization method
    if api == 'eloqua':
        headers = {'Authorization': 'Basic ' + eloqua_auth}
    elif api == 'click':
        click_api_key = pickle.load(open(file('click'), 'rb'))
        headers = {'X-Api-Key': click_api_key}

    # Assings correct api call
    if call == 'get':
        response = requests.get(
            root,
            headers=headers)
    elif call == 'post':
        headers['Content-Type'] = 'application/json'
        response = requests.post(
            root,
            headers=headers,
            data=data)

    # Prints status code
    if status:
        status_code(response, root)

    return response


'''
=================================================================================
                                Eloqua Authentication
=================================================================================
'''


def get_eloqua_auth():
    '''
    Returns:
    1. Eloqua API Key needed for authorization.
    2. Eloqua Root URL
    3. User name
    '''
    def get_eloqua_root(eloqua_auth):
        '''
        Returns Eloqua base URL for your instance.
        '''
        root = 'https://login.eloqua.com/id'
        response = api_request(root=root, eloqua_auth=eloqua_auth)
        login_data = response.json()

        return login_data

    while True:
        # Gets Eloqua user details if they are already stored
        if not os.path.isfile(file('eloqua')):
            print(f'{Fore.YELLOW}» {Fore.WHITE}Enter Eloqua Company name: ', end='')
            eloqua_domain = input(' ')
            print(f'{Fore.YELLOW}» {Fore.WHITE}Enter Eloqua User name: ', end='')
            eloqua_user = input(' ')
            eloqua_auth = (eloqua_domain, eloqua_user)
            pickle.dump(eloqua_auth, open(file('eloqua'), 'wb'))
        eloqua_domain, eloqua_user = pickle.load(open(file('eloqua'), 'rb'))
        print(f'{Fore.YELLOW}» {Fore.WHITE}Enter Eloqua Password: ', end='')
        eloqua_password = getpass.getpass(' ')

        # Converts domain, user and  to Eloqua Auth Key
        eloqua_api_key = bytes(eloqua_domain + '\\' +
                               eloqua_user + ':' +
                               eloqua_password, 'utf-8')
        eloqua_api_key = str(base64.b64encode(eloqua_api_key), 'utf-8')

        # Gets Eloqua root URL
        try:
            login_data = get_eloqua_root(eloqua_api_key)
            eloqua_root = login_data['urls']['base']
        except TypeError:
            print(f'{Fore.RED}[ERROR] {Fore.YELLOW}Login failed!')
            os.remove(file('eloqua'))
            continue
        if eloqua_root:
            break

    return (eloqua_api_key, eloqua_root)


'''
=================================================================================
                                Eloqua Authentication
=================================================================================
'''


def get_click_auth():
    '''
    Returns ClickMeeting API Key needed for authorization
    '''
    if not os.path.isfile(file('click')):
        while True:
            print(
                f'\n{Fore.WHITE}Copy ClickMeeting API Key [CTRL+C] and click [Enter]', end='')
            input(' ')
            click_api_key = pyperclip.paste()
            if len(click_api_key) == 42:
                break
            else:
                print(f'{Fore.RED}[ERROR] {Fore.YELLOW}Incorrect API Key!')
        pickle.dump(click_api_key, open(file('click'), 'wb'))
    click_api_key = pickle.load(open(file('click'), 'rb'))

    return click_api_key
