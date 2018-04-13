#!/usr/bin/env python3.6
# -*- coding: utf8 -*-

'''
ELQuent.api
Eloqua API functions for other modules

Mateusz Dąbrowski
github.com/MateuszDabrowski
linkedin.com/in/mateusz-dabrowski-marketing/
'''

# Python imports
import os
import sys
import json
import time
import base64
import pickle
import getpass
import requests
import encodings
from colorama import Fore, init

# Initialize colorama
init(autoreset=True)

# If you want to print API connection status codes, set debug to True
DEBUG = False


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
            return os.path.join(datadir, 'utils', 'api', filename)
        else:
            datadir = os.path.dirname(os.path.dirname(__file__))
            return os.path.join(datadir, 'api', filename)

    file_paths = {
        'click': find_data_file('click.p'),
        'eloqua': find_data_file('eloqua.p'),
        'country': find_data_file('country.p'),
        'naming': find_data_file('naming.json')
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


def api_request(root, call='get', api='eloqua', status=DEBUG, data={}):
    '''
    Arguments:
        root - root URL of API call
        call - either GET or POST
        api - either elouqa or click
    Returns response from Eloqua API call.
    '''

    # Assings correct authorization method
    if api == 'eloqua':
        headers = {'Authorization': 'Basic ' + eloqua_key}
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
    Returns Eloqua Root URL and creates globals with auth and bulk/rest roots
    '''
    def get_eloqua_root(eloqua_auth):
        '''
        Returns Eloqua base URL for your instance.
        '''
        root = 'https://login.eloqua.com/id'
        response = api_request(root=root)
        login_data = response.json()

        return login_data

    while True:
        # Gets Eloqua user details if they are already stored
        print()
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
        global eloqua_key
        eloqua_key = bytes(eloqua_domain + '\\' +
                           eloqua_user + ':' +
                           eloqua_password, 'utf-8')
        eloqua_key = str(base64.b64encode(eloqua_key), 'utf-8')

        # Gets Eloqua root URL
        try:
            login_data = get_eloqua_root(eloqua_key)
            eloqua_root = login_data['urls']['base']
        except TypeError:
            print(f'{Fore.RED}[ERROR] {Fore.YELLOW}Login failed!')
            os.remove(file('eloqua'))
            continue
        if eloqua_root:
            break

    # Creates globals related to Eloqua API
    global eloqua_bulk
    eloqua_bulk = eloqua_root + '/api/BULK/2.0/'
    global eloqua_rest
    eloqua_rest = eloqua_root + '/api/REST/1.0/'

    return eloqua_root


'''
=================================================================================
                            Upload Contacts API Flow
=================================================================================
'''


def eloqua_create_sharedlist(export):
    '''
    Creates shared list for contacts
    Requires 'export' dict with webinars and conctacts in format:
    {'listName': ['mail', 'mail']}
    '''
    outcome = []
    print(f'\n{Fore.BLUE}Saving to shared list:', end='')

    # Unpacks export
    for name, contacts in export.items():
        root = f'{eloqua_rest}assets/contact/list'
        data = {'name': f'{name}',
                'description': 'ELQuent API Upload',
                'folderId': f'{shared_list}'}
        response = api_request(
            root, call='post', data=json.dumps(data))
        sharedlist = response.json()

        print(
            f'\n{Fore.WHITE}» [{Fore.YELLOW}{len(contacts)}{Fore.WHITE}] {name}')
        # Simple shared list creation
        if response.status_code == 201:
            print(f'{Fore.GREEN}  [Created]', end=' ')
            list_id = int(sharedlist['id'])
        # Shared list already exists - appending data
        else:
            print(f'{Fore.YELLOW}  [Exists]{Fore.GREEN} » [Append]', end=' ')
            list_id = sharedlist[0]['requirement']['conflictingId']

        uri = eloqua_import_definition(name, list_id)
        count = eloqua_import_content(contacts, list_id, uri)
        status = eloqua_import_sync(uri)
        outcome.append((list_id, name, count, status))

    return outcome


def eloqua_import_definition(name, list_id):
    '''
    Request to obtain uri key for data upload
    Requires name of import and ID of shared list
    Returns uri key needed for data upload
    '''
    data = {'name': name,
            'fields': {
                'SourceCountry': '{{Contact.Field(C_Source_Country1)}}',
                'EmailAddress': '{{Contact.Field(C_EmailAddress)}}'},
            'identifierFieldName': 'EmailAddress',
            'isSyncTriggeredOnImport': 'false',
            'syncActions': {
                'action': 'add',
                'destination': '{{ContactList[%s]}}' % list_id}}
    root = eloqua_bulk + 'contacts/imports'
    response = api_request(root, call='post', data=json.dumps(data))
    import_eloqua = response.json()
    uri = import_eloqua['uri'][1:]

    return uri


def eloqua_import_content(contacts, list_id, uri):
    '''
    Uploads contacts from ClickWebinar to Eloqua
    Requires list of contacts for upload, shared list ID and uri key
    Returns count of uploaded contacts
    '''
    count = 0
    upload = []
    record = {}
    for user in contacts:
        record = {'SourceCountry': source_country,
                  'EmailAddress': user}
        upload.append(record)
        count += 1
    root = eloqua_bulk + uri + '/data'
    api_request(root, call='post', data=json.dumps(upload))

    return count


def eloqua_import_sync(uri):
    '''
    Requests to sync import
    Checks status of sync
    Requires uri key
    Returns status of sync
    '''

    # Requests sync
    root = eloqua_bulk + 'syncs'
    sync_body = {'syncedInstanceUri': f'/{uri}'}
    response = api_request(root, call='post', data=json.dumps(sync_body))
    sync_eloqua = response.json()

    # Checks stats of sync
    sync_uri = sync_eloqua['uri']
    status = sync_eloqua['status']
    while status != 'success':
        root = eloqua_bulk + sync_uri
        sync_body = {'syncedInstanceUri': f'/{sync_uri}'}
        response = api_request(root)
        sync_status = response.json()
        status = sync_status['status']
        print(f'{Fore.BLUE}{status}/', end='', flush=True)
        if status == 'warning' or status == 'error':
            logs = eloqua_log_sync(uri)
            print(logs)
            break
        time.sleep(3)

    return status


def eloqua_log_sync(uri):
    '''
    Shows log for problematic sync
    Requires uri key to get id of sync
    Returns logs of sync
    '''
    id = uri[-5:]
    root = eloqua_bulk + f'syncs/{id}/logs'
    response = api_request(root)
    logs_eloqua = response.json()

    return logs_eloqua


'''
=================================================================================
                            Main Eloqua API Flows
=================================================================================
'''


def upload_contacts(country, contacts, sharedlist):
    '''
    Contacts argument should be dict with list: {'listName': ['mail', 'mail']}
    Uploads mail list to Eloqua as shared list listName (appends if it already exists)
    '''
    # Creates global source_country from main module
    global source_country
    source_country = country

    # Gets auth and global values
    get_eloqua_auth()

    # Gets data from naming.json
    with open(file('naming'), 'r', encoding='utf-8') as f:
        global naming
        naming = json.load(f)

    # Creates global shared_list information from json
    global shared_list
    shared_list = naming[source_country][sharedlist]['sharedlist']

    # Uploads database to eloqua shared list
    eloqua_create_sharedlist(contacts)

    return True


'''
TODO:
- asking in case of possible overwrite of shared list (with global switch)
'''
