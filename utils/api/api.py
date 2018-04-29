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
import re
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
from collections import defaultdict

# Initialize colorama
init(autoreset=True)

# Predefined messege elements
ERROR = f'{Fore.WHITE}[{Fore.RED}ERROR{Fore.WHITE}] {Fore.YELLOW}'
WARNING = f'{Fore.WHITE}[{Fore.YELLOW}ERROR{Fore.WHITE}] '
SUCCESS = f'{Fore.WHITE}[{Fore.GREEN}SUCCESS{Fore.WHITE}] '

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
                                Eloqua Asset Helpers
=================================================================================
'''


def get_asset_id(asset):
    '''
    Returns valid ID of chosen Eloqua asset
    '''

    assets = {
        'LP': 'Landing Page',
        'Form': 'Form',
        'Mail': 'E-mail'
    }

    asset_name = assets.get(asset)

    while True:
        print(
            f'\n{Fore.WHITE}» [{Fore.YELLOW}{asset}{Fore.WHITE}] Write or paste {asset_name} ID and click [Enter] or use [C]lipboard', end='')
        asset_id = input(' ')

        # Skips to get code via pyperclip
        if asset_id.lower() == 'c':
            return None

        # Checks if input in numerical value
        try:
            asset_id = int(asset_id)
        except ValueError:
            print(f'{ERROR}It is not valid Eloqua {asset_name} ID')
            continue

        # Checks if there is asset with that ID
        try:
            if asset == 'LP':
                asset_exists = eloqua_get_landingpage(asset_id)
            elif asset == 'Form':
                asset_exists = eloqua_get_form(asset_id)
            elif asset == 'Mail':
                asset_exists = eloqua_get_email(asset_id)
        except json.decoder.JSONDecodeError:
            asset_exists = False

        # Gets ID confirmation from user
        if asset_exists:
            choice = ''
            while choice.lower() != 'y' and choice.lower() != 'n':
                print(
                    f'{Fore.WHITE}» Continue with {Fore.YELLOW}{asset_exists[0]}{Fore.WHITE}? ({Fore.GREEN}y{Fore.WHITE}/{Fore.RED}n{Fore.WHITE}):', end='')
                choice = input(' ')
            if choice.lower() == 'y':
                return asset_id
            elif choice.lower() == 'n':
                get_asset_id(asset)
        else:
            print(f'{ERROR}Not found Eloqua {asset_name} with given ID')


def eloqua_asset_exist(name, asset):
    '''
    Returns True if there is already asset in Eloqua instance with that name
    '''

    assets = {
        'LP': 'landingPages',
        'Form': 'forms',
        'Mail': 'emails'
    }

    endpoint = assets.get(asset)
    # Gets data of requested image name
    root = f'{eloqua_rest}assets/{endpoint}'
    params = {'search': name}
    response = api_request(root, params=params)
    elq_asset = response.json()

    if elq_asset['total']:
        id = elq_asset['elements'][0]['id']
        print(
            f'\n  {WARNING}{asset} "{name}" already exists! [ID: {id}]')
        while True:
            print(
                f'  {Fore.WHITE}» Click [Enter] to continue with current name or [Q] to quit', end='')
            choice = input(' ')
            if not choice:
                return id
            elif choice.lower() == 'q':
                print(f'\n{Fore.GREEN}Ahoj!')
                raise SystemExit
            else:
                print(
                    f'\n{ERROR}Entered value is not a valid choice!')
    else:
        return False


def eloqua_asset_html_name(name):
    '''
    Returns correct html_name for the asset
    '''
    html_name = ''
    date_element = re.compile(r'\d\d', re.UNICODE)
    local_name = name.split('_')[-2]  # Gets local name from asset name
    for part in local_name.split('-'):
        # Skip if part belongs to PSP
        if part.startswith(tuple(naming[source_country]['psp'])):
            continue
        # Skip if part is a date
        elif date_element.search(part):
            continue
        else:
            html_name += f'{part}-'
    # Gets asset type last part of html_name
    html_name += name.split('_')[-1]

    return html_name


def eloqua_asset_name():
    '''
    Returns correct name for the asset
    '''
    while True:
        name = input(' ')
        name_check = name.split('_')
        if len(name_check) != 5:
            print(
                f'{ERROR}Expected 5 name elements, found {len(name_check)}')
        elif name_check[0][:2] != 'WK':
            print(
                f'{ERROR}"{name_check[0]}" is not existing country code')
        elif name_check[1] not in naming[source_country]['segment']:
            print(
                f'{ERROR}"{name_check[1]}" is not existing segment name')
        elif name_check[2] not in naming['campaign']:
            print(
                f'{ERROR}"{name_check[2]}" is not existing campaign type')
        else:
            return name
        print(f'{Fore.YELLOW}Please write or paste correct name:')


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
    elif call == 'put':
        headers['Content-Type'] = 'application/json'
        response = requests.put(
            root,
            headers=headers,
            data=data)
    elif call == 'delete':
        headers['Content-Type'] = 'application/json'
        response = requests.delete(root, headers=headers)

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
            print(f'{ERROR}Login failed!')
            os.remove(file('eloqua'))
            continue
        if eloqua_root:
            break

    # Creates globals related to Eloqua API
    global eloqua_bulk
    eloqua_bulk = eloqua_root + '/api/BULK/2.0/'
    global eloqua_rest
    eloqua_rest = eloqua_root + '/api/REST/2.0/'

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
        if status == 'success':
            # Sync_id is syncedInstanceUri from sync response
            import_id = (uri.split('/'))[-1]
            root = eloqua_bulk + f'contacts/imports/{import_id}'
            response = api_request(root, call='delete')
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
    while True:
        root = eloqua_bulk + sync_uri
        sync_body = {'syncedInstanceUri': f'/{sync_uri}'}
        response = api_request(root)
        sync_status = response.json()
        status = sync_status['status']
        print(f'{Fore.BLUE}{status}/', end='', flush=True)
        if status in ['warning', 'error', 'success']:
            eloqua_log_sync(sync_uri)
            break
        time.sleep(5)

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
            print(f'\t{Fore.YELLOW}› {item["count"]} {item["message"]}')
        if item['message'] in ['Contacts created.', 'Contacts updated.']:
            print(f'\t{Fore.GREEN}› {item["count"]} {item["message"]}')
    return logs_eloqua


'''
=================================================================================
                                Landing Page API
=================================================================================
'''


def eloqua_get_landingpage(id):
    '''
    Returns name and code of Landing Page of given ID
    '''
    # Gets data of requested image name
    root = f'{eloqua_rest}assets/landingPage/{id}'
    params = {'depth': 'complete'}
    response = api_request(root, params=params)
    landing_page = response.json()

    name = landing_page['name']
    code = landing_page['htmlContent']['html']
    return (name, code)


def eloqua_create_landingpage(name, code):
    '''
    Requires name and code of the landing page to create LP in Eloqua
    Returns Landing Page ID
    '''
    # Adds source contry to received asset name
    name = f'WK{source_country}_{name}'

    # Checks if there already is LP with that name
    eloqua_asset_exist(name, asset='LP')

    # Chosses correct folder ID for upload
    segment = name.split('_')[1]
    folder_id = naming[source_country]['id']['landingpage'].get(segment)

    # Creates correct html_name
    html_name = eloqua_asset_html_name(name)

    # Gets id and url of microsite
    microsite_id = naming[source_country]['id']['microsite'][0]
    microsite_link = naming[source_country]['id']['microsite'][1]

    while True:
        # Creating a post call to Eloqua API
        root = f'{eloqua_rest}assets/landingPage'
        data = {
            'name': name,  # asset name
            'description': 'ELQuent API Upload',
            'folderId': folder_id,
            'micrositeId': microsite_id,  # html name domain
            'relativePath': f'/{html_name}',  # html name path
            'htmlContent': {
                'type': 'RawHtmlContent',
                'html': code
            }
        }
        response = api_request(
            root, call='post', data=json.dumps(data))
        landing_page = response.json()

        # Checks if there is error
        if type(landing_page) is list and len(landing_page) == 1 and landing_page[0]['type'] == 'ObjectValidationError' and landing_page[0]['property'] == 'relativePath' and landing_page[0]['requirement']['type'] == 'UniquenessRequirement':
            print(
                f'\n  {ERROR}URL ending "/{html_name}" already exists!',
                f'\n  {Fore.WHITE}» Enter new URL ending:', end='')
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
    print(f'{Fore.WHITE}» {SUCCESS}Created Eloqua Landing Page ID: {id}')
    webbrowser.open(url)

    return (id, url)


'''
=================================================================================
                                    Form API
=================================================================================
'''


def eloqua_get_form(id, depth=''):
    '''
    Returns name and code of Form of given ID
    '''
    # Gets data of requested image name
    root = f'{eloqua_rest}assets/form/{id}'
    params = {'depth': 'complete'}
    response = api_request(root, params=params)
    form = response.json()

    if depth == 'complete':
        return form

    name = form['name']
    code = form['html']
    return (name, code)


def eloqua_create_form(name, data):
    '''
    Requires name, json data and version of the form to create it in Eloqua
    Returns Form ID
    '''
    # Checks if there already is Form with that name
    eloqua_asset_exist(name, asset='Form')

    # Creating a post call to Eloqua API
    root = f'{eloqua_rest}assets/form'
    response = api_request(
        root, call='post', data=json.dumps(data))
    form = response.json()

    # Open in new tab
    id = form['id']
    print(f'{Fore.WHITE}» {SUCCESS}Created Eloqua Form ID: {id}')

    return (id, form)


def eloqua_update_form(id, css='', html='', processing={}):
    '''
    Requires id and json data of the form to update it in Eloqua
    Returns Form ID
    '''
    # Gets current data of form to update
    data = eloqua_get_form(id, depth='complete')
    if css:
        data['customCSS'] = css
    if html:
        data['html'] = html
    if processing:
        data['processingSteps'] = processing

    # Creating a post call to Eloqua API and taking care of emoticons encoding
    root = f'{eloqua_rest}assets/form/{id}'
    response = api_request(
        root, call='put', data=json.dumps(data))
    form = response.json()

    # Open in new tab
    id = form['id']
    url = naming['root'] + '#forms&id=' + id
    print(
        f'{Fore.WHITE}» {SUCCESS}Updated Eloqua Form ID: {id}')
    webbrowser.open(url)

    return id


'''
=================================================================================
                                    E-mail API
=================================================================================
'''


def eloqua_get_email_group(mail_name):
    '''
    Returns chosen email group ID
    '''
    # Gets data of requested image name
    root = f'{eloqua_rest}assets/email/groups'
    params = {'depth': 'minimal',
              'search': f'WK{source_country}*'}
    response = api_request(root, params=params)
    email_groups_response = response.json()

    # Tries to automatically select group based on naming
    mail_name_parts = mail_name.split('_')
    local_name_parts = (mail_name_parts[3]).split('-')
    try:
        id = naming[source_country]['mail']['data'][local_name_parts[0]]['group_id']
        return id
    except KeyError:
        if mail_name_parts[1:3] == ['PROF', 'BOO']:
            return naming[source_country]['mail']['data']['Profinfo']['group_id']

    email_groups = []
    for group in email_groups_response['elements']:
        # Skips email groups waiting for deletion
        if 'delete' in group['name'].lower():
            continue
        name = group['name'].split(' - ')
        # Skips email groups checked in above part
        if name[1].lower() in ['newsletter', 'alert', 'profinfo']:
            continue
        if len(name) == 2:
            name = [name[-1]]
        if len(name) == 3:
            name = [name[-2], name[-1]]
        email_groups.append((name, group['id']))
    email_groups.sort()

    # Prints first level of email groups and single-level email groups
    print(f'\n{Fore.GREEN}Choose Email Group:')
    for i, group in enumerate(email_groups):
        print(f'{Fore.WHITE}[{Fore.YELLOW}{i}{Fore.WHITE}]\t» ', end='')
        if len(group[0]) == 1:
            print(f'{Fore.WHITE}{group[0][0]}')
        if len(group[0]) == 2:
            print(f'{Fore.YELLOW}{group[0][0]}{Fore.WHITE} › {group[0][1]}')

    # Returns id of email group chosen by user
    while True:
        print(
            f'{Fore.YELLOW}Enter number associated with chosen email group:', end='')
        choice = input(' ')
        try:
            choice = int(choice)
        except (TypeError, ValueError):
            print(f'{Fore.RED}Please enter numeric value!')
            choice = ''
            continue
        if 0 <= choice < len(email_groups):
            id = email_groups[choice]
            return id[1]
        else:
            print(f'{Fore.RED}Entered value does not belong to any email group!')
            choice = ''


def eloqua_get_email(id, depth=''):
    '''
    Returns name and code of E-mail of given ID or full response if depth='complete'
    '''
    # Gets data of requested image name
    root = f'{eloqua_rest}assets/email/{id}'
    params = {'depth': 'complete'}
    response = api_request(root, params=params)
    email = response.json()

    if depth == 'complete':
        return email

    name = email['name']
    code = email['htmlContent']['html']
    return (name, code)


def eloqua_search_emails(phrase):
    '''
    Returns information about e-mails with phrase
    '''
    # Gets data of requested image name
    root = f'{eloqua_rest}assets/emails'
    params = {'depth': 'complete',
              'search': f'{phrase}*',
              'orderBy': 'id DESC',
              'count': '5'}
    response = api_request(root, params=params)
    email = response.json()

    return email


def eloqua_fill_mail_params(name):
    '''
    Returns eloqua_create_email data based on settings of similar mails from the past
    '''
    # Start building data dict
    data = {}
    data['name'] = name
    data['description'] = 'ELQuent API Upload'
    data['bounceBackEmail'] = naming[source_country]['mail']['bounceback']
    data['replyToName'] = naming[source_country]['mail']['reply_name']
    data['isTracked'] = 'true'
    # data['subject'] = subject

    # Builds search name to use as param
    name_split = name.split('_')
    global_name = ('_').join(name_split[:3])
    local_name = name_split[3].split('-')
    search_name = f'{global_name}_{local_name[0]}'
    previous_mails = eloqua_search_emails(search_name)

    # Builds gatherers for data from found similar emails
    sender_mail = []
    sender_name = []
    reply_mail = []
    folder_id = []
    footer = []
    header = []
    group_id = []

    # Fills gatherers with data
    for mail in previous_mails['elements']:
        sender_mail.append(mail['senderEmail'])
        sender_name.append(mail['senderName'])
        reply_mail.append(mail['replyToEmail'])
        folder_id.append(mail['folderId'])
        footer.append(mail['emailFooterId'])
        header.append(mail['emailHeaderId'])
        group_id.append(mail['emailGroupId'])

    # Deduplication to check if there is pattern
    sender_mail = list(set(sender_mail))
    sender_name = list(set(sender_name))
    reply_mail = list(set(reply_mail))
    folder_id = list(set(folder_id))
    footer = list(set(footer))
    header = list(set(header))
    group_id = list(set(group_id))

    # If there is single pattern, use this for import
    chosen_sender = ''  # Allows to propageate chosen sender as reply address
    if len(sender_mail) == 1:
        data['senderEmail'] = sender_mail[0]
    else:
        for i, sender in enumerate(sender_mail):
            print(f'{Fore.WHITE}[{Fore.YELLOW}{i}{Fore.WHITE}]\t» {sender}')
        print(
            f'{Fore.WHITE}[{Fore.YELLOW}S{Fore.WHITE}]\t» Skip choosing sender e-mail')
        # Returns sender e-mail choosen by user
        while True:
            print(
                f'{Fore.YELLOW}Enter number associated with chosen sender e-mail:', end='')
            choice = input(' ')
            if choice.lower() == 's':
                print(
                    f'{WARNING}Sender e-mail empty')
                break
            try:
                choice = int(choice)
            except (TypeError, ValueError):
                print(f'{Fore.RED}Please enter numeric value!')
                choice = ''
                continue
            if 0 <= choice < len(sender_mail):
                chosen_sender = sender_mail[choice]
                break
            else:
                print(
                    f'{Fore.RED}Entered value does not belong to any email address!')
                choice = ''

    if len(sender_name) == 1:
        data['senderName'] = sender_name[0]
    else:
        data['senderName'] = 'Wolters Kluwer'

    if len(reply_mail) == 1:
        data['replyToEmail'] = reply_mail[0]
    elif chosen_sender:
        data['replyToEmail'] = chosen_sender
    else:
        print(f'{WARNING}Reply e-mail not found')

    if len(folder_id) == 1:
        data['folderId'] = folder_id[0]
    else:
        id = naming[source_country]['id']['email'].get(
            name_split[1], naming[source_country]['id']['email'].get(source_country))
        data['folderId'] = id

    if len(footer) == 1:
        data['emailFooterId'] = footer[0]
    else:
        print(f'{WARNING}Email footer not found')

    if len(header) == 1:
        data['emailHeaderId'] = sender_mail[0]
    else:
        print(f'{WARNING}Email header not found')

    if len(group_id) == 1:
        data['emailGroupId'] = sender_mail[0]
    else:
        group_id = eloqua_get_email_group(name)
        data['emailGroupId'] = group_id

    return data


def eloqua_create_email(name, code):
    '''
    Requires name and code of the email to create it in Eloqua
    Returns E-mail ID
    '''
    # Adds source contry to received asset name
    name = f'WK{source_country}_{name}'

    # Checks if there already is E-mail with that name
    eloqua_asset_exist(name, asset='Mail')

    # Gets required data for the API call
    data = eloqua_fill_mail_params(name)
    data['isTracked'] = 'true'
    data['htmlContent'] = {
        'type': 'RawHtmlContent',
        'html': code
    }

    # Creating a post call to Eloqua API
    root = f'{eloqua_rest}assets/email'
    response = api_request(
        root, call='post', data=json.dumps(data))
    email = response.json()

    # Open in new tab
    id = email['id']
    url = naming['root'] + '#emails&id=' + id
    print(
        f'\n{Fore.WHITE}» {SUCCESS}Created Eloqua E-mail ID: {id}')
    webbrowser.open(url)

    return id


def eloqua_update_email(id, code):
    '''
    Requires id and code of the email to update it in Eloqua
    Returns E-mail ID
    '''
    # Gets current data of e-mail to update
    old_data = eloqua_get_email(id, depth='complete')
    code = code.replace('"', '\"')
    data = {
        'type': 'Email',
        'isTracked': 'true',
        'htmlContent': {
            'type': 'RawHtmlContent',
            'html': code
        }
    }

    # Takes care of case where there is lack of element in source mail
    for element in ['currentStatus', 'id', 'createdAt', 'createdBy', 'folderId', 'name', 'updatedAt', 'updatedBy', 'bounceBackEmail', 'emailFooterId', 'emailGroupId', 'emailHeaderId', 'replyToEmail', 'replyToName', 'senderEmail', 'senderName', 'subject']:
        try:
            data[element] = old_data[element]
        except KeyError:
            continue

    # Creating a post call to Eloqua API and taking care of emoticons encoding
    root = f'{eloqua_rest}assets/email/{id}'
    response = api_request(
        root, call='put', data=json.dumps(data, ensure_ascii=False).encode('utf-8'))
    email = response.json()

    # Open in new tab
    id = email['id']
    url = naming['root'] + '#emails&id=' + id
    print(
        f'\n{Fore.WHITE}[{Fore.YELLOW}UPDATED{Fore.WHITE}] Eloqua E-mail ID: {id}')
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

    # Gets data of requested image name
    root = f'{eloqua_rest}assets/images'
    params = {'depth': 'complete',
              'orderBy': 'createdAt Desc',
              'search': image_name}
    response = api_request(root, params=params)
    image_info = response.json()
    image_link = image_info['elements'][0]['fullImageUrl']
    image_link = (image_link.split('/'))[-1]
    image_link = naming['image'] + image_link

    # Warns if there are multiple images found by query
    if int(image_info['total']) > 1:
        print(
            f'\n{WARNING}More then one image found - adding newest ', end='')

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
