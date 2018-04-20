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
import webbrowser
from colorama import Fore, init

# Initialize colorama
init(autoreset=True)

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


def api_request(root, call='get', api='eloqua', params={}, debug=False, data={}):
    '''
    Arguments:
        root - root URL of API call
        call - either GET or POST
        api - either elouqa or click
    Returns response from Eloqua API call.

    If you want to print API connection status codes, set debug to True
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
            headers=headers,
            params=params)
    elif call == 'post':
        headers['Content-Type'] = 'application/json'
        response = requests.post(
            root,
            headers=headers,
            data=data)

    # Prints status code
    if debug:
        status_code(response, root)

    return response


'''
=================================================================================
                                Eloqua Authentication
=================================================================================
'''


def get_eloqua_auth(country):
    '''
    Returns Eloqua Root URL and creates globals with auth and bulk/rest roots
    '''

    # Creates global source_country from main module
    global source_country
    source_country = country

    # Gets data from naming.json
    with open(file('naming'), 'r', encoding='utf-8') as f:
        global naming
        naming = json.load(f)

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


def eloqua_create_sharedlist(export, choice):
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
        # Shared list already exists
        else:
            while True:  # Asks user what to do next
                if not choice:
                    print(f'\n{Fore.YELLOW}Shared list with that name already exist.',
                          f'\n{Fore.WHITE}[{Fore.YELLOW}0{Fore.WHITE}]\tStop importing to Eloqua',
                          f'\n{Fore.WHITE}[{Fore.YELLOW}1{Fore.WHITE}]\tAppend contacts to existing shared list')
                    if len(export) == 1:
                        print(
                            f'{Fore.WHITE}[{Fore.YELLOW}2{Fore.WHITE}]\tChange upload name')
                    print(
                        f'{Fore.WHITE}Enter number associated with your choice:', end='')
                    choice = input(' ')
                if not choice or choice == '0':  # Dropping import
                    return False
                elif choice == '1' or choice == 'append':  # Appending data to existing shared list
                    print(
                        f'{Fore.YELLOW}  [Exists]{Fore.GREEN} » [Append]', end=' ')
                    list_id = sharedlist[0]['requirement']['conflictingId']
                    break
                # Changing name and trying again
                elif choice == '2' and len(export) == 1:
                    name_split = name.split('_')
                    print(
                        f'\n{Fore.WHITE}» Write different name ending for the shared list upload: ', end='')
                    ending = input(' ')
                    new_name = '_'.join(name_split[:4] + [ending])
                    new_export = {new_name: contacts}
                    outcome = eloqua_create_sharedlist(new_export, '')
                    return outcome

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
            eloqua_log_sync(sync_uri)
            break
        time.sleep(3)
    print()

    return status


def eloqua_log_sync(sync_uri):
    '''
    Shows log for problematic sync
    Requires uri key to get id of sync
    Returns logs of sync
    '''
    print(f'{Fore.WHITE}{sync_uri[1:]}')
    id = (sync_uri.split('/'))[-1]
    root = eloqua_bulk + f'syncs/{id}/logs'
    response = api_request(root)
    logs_eloqua = response.json()
    for item in logs_eloqua['items']:
        if item['severity'] == 'warning':
            print(f'\t{Fore.YELLOW}» {item["count"]} {item["message"]}')
        if item['message'] in ['Contacts created.', 'Contacts updated.']:
            print(f'\t{Fore.GREEN}» {item["count"]} {item["message"]}')

    return logs_eloqua


'''
=================================================================================
                                    Upload LP API
=================================================================================
'''


def eloqua_create_landingpage(name, code):
    '''
    Requires name and code of the landing page to create LP in Eloqua
    Returns Landing Page ID

    TODO: Checking if there is LP with the same name
    '''
    # Chosses correct folder ID for upload
    segment = name.split('_')[0]
    folder_id = naming[source_country]['id']['landingpage'].get(segment)

    # Creates correct html_name
    local_name = name.split('_')[-2]  # Gets local name from asset name
    local_name = local_name.split('-')[:-5]  # Cuts down date & PSP elements
    local_name = '-'.join(local_name)  # Local name concat
    lp_type = name.split('_')[-1]  # Gets last part of asset name as asset type
    html_name = f'{local_name}-{lp_type}'

    # Gets id and url of microsite
    microsite_id = naming[source_country]['id']['microsite'][0]
    microsite_link = naming[source_country]['id']['microsite'][1]

    while True:
        # Creating a post call to Eloqua API
        root = f'{eloqua_rest}assets/landingPage'
        data = {
            'name': name,  # asset name
            'description': 'ELQuent API Upload',  # asset description
            'folderId': folder_id,  # folder id
            'micrositeId': microsite_id,  # html name domain
            'relativePath': f'/{html_name}',  # html name path
            'htmlContent': {
                'type': 'RawHtmlContent',
                'metaTags': [],
                'html': code
            }
        }
        response = api_request(
            root, call='post', data=json.dumps(data))
        landing_page = (response.json())
        print(landing_page)
        # Checks if there is error
        if type(landing_page) is list and len(landing_page) == 1 and landing_page[0]['type'] == 'ObjectValidationError' and landing_page[0]['property'] == 'relativePath' and landing_page[0]['requirement']['type'] == 'UniquenessRequirement':
            print(
                f'  {Fore.RED}[ERROR] {Fore.YELLOW} URL ending "/{html_name}" already exists!',
                f'\n{Fore.WHITE}» Enter new URL ending:', end='')
            html_name = input(' ')
            continue
        elif type(landing_page) is list:  # Other errors
            print(f'{Fore.YELLOW}{landing_page}')
        elif landing_page['type'] == 'LandingPage':
            break
        else:  # Weird cases
            print(f'{Fore.YELLOW}{landing_page}')

    # Open in new tab
    id = landing_page['id']
    url = microsite_link + landing_page['relativePath']
    print(
        f'{Fore.WHITE}» [{Fore.YELLOW}CREATED{Fore.WHITE}] LP in Eloqua with ID {id}')
    webbrowser.open(url)

    return id


'''
=================================================================================
                                Image URL Getter API
=================================================================================
'''


def eloqua_get_image(image_name):
    '''
    Returns url of uploaded image
    '''

    # Gets data on that
    root = f'{eloqua_rest}assets/images'
    payload = {'depth': 'complete',
               'orderBy': 'createdAt Desc',
               'search': image_name}
    response = api_request(root, params=payload)
    image_info = response.json()
    image_link = image_info['elements'][0]['fullImageUrl']
    image_link = (image_link.split('/'))[-1]
    image_link = naming['image'] + image_link

    # Warns if there are multiple images found by query
    if int(image_info['total']) > 1:
        print(
            f'\n{Fore.YELLOW}[WARNING] {Fore.WHITE}More then one image found - adding newest ', end='')
    return image_link


'''
=================================================================================
                            Main Eloqua API Flows
=================================================================================
'''


def upload_contacts(contacts, list_type, choice=''):
    '''
    Contacts argument should be dict with list: {'listName': ['mail', 'mail']}
    Uploads mail list to Eloqua as shared list listName (appends if it already exists)
    '''

    # Creates global shared_list information from json
    global shared_list
    shared_list = naming[source_country]['id']['sharedlist'][list_type]

    # Uploads database to eloqua shared list
    eloqua_create_sharedlist(contacts, choice)

    return
