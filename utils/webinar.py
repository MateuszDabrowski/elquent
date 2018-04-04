#!/usr/bin/env python3.6

'''
ELQuent.webinar
Gets attendees and registered users from ClickMeeting 
and uploads them to Oracle Eloqua as shared list

Mateusz Dąbrowski
github.com/MateuszDabrowski
linkedin.com/in/mateusz-dabrowski-marketing/
'''

import os
import sys
import json
import time
import base64
import getpass
import datetime
import requests
from colorama import Fore, init

# Initialize colorama
init(autoreset=True)

# If you want to print API connection status codes, set debug to True
DEBUG = False


def file(file_path, name='LP'):
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
        'naming': find_data_file('naming.json')
    }

    return file_paths.get(file_path)


'''
=================================================================================
                            General use functions
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
        headers = {'X-Api-Key': click_key}

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
                        ClickMeeting API specific functions
=================================================================================
'''


def click_export_rooms():
    '''
    Returns ClickMeeting ID's and names of active and inactive rooms
    '''

    room_ids = []
    room_names = []

    # Save active rooms
    root = click_root + 'conferences/active'
    response = api_request(root, eloqua_auth=eloqua_key, api='click')
    rooms_active_click = response.json()
    for room in rooms_active_click:
        room_ids.append(room['id'])
        room_names.append(room['name'])

    # Save inactive rooms
    root = click_root + 'conferences/inactive'
    response = api_request(root, eloqua_auth=eloqua_key, api='click')
    rooms_inactive_click = response.json()
    for room in rooms_inactive_click:
        room_ids.append(room['id'])
        room_names.append(room['name'])
    click_rooms = list(zip(room_ids, room_names))

# <Company specific code> =========================================================================
    # Filter out internal webinars from export
    internal_webinars = naming[source_country]['webinar']['filters']
    for filtering in internal_webinars:
        click_rooms = [(id, name) for (id, name)
                       in click_rooms if f'{filtering}' not in name.lower()]
# ========================================================================= </Company specific code>

    return click_rooms


def click_export_sessions(click_rooms):
    '''
    Returns ClickMeeting sessions for active and inactive rooms
    '''

    click_sessions = {}

    # Save all sessions
    for room in click_rooms:
        root = f'{click_root}conferences/{room[0]}/sessions'
        response = api_request(root, eloqua_auth=eloqua_key, api='click')
        if response.status_code == 200:
            print(f'{Fore.GREEN}|', end='', flush=True)
            sessions_in_room = response.json()
            for session in sessions_in_room:
                click_session = (session['id'], session['end_date'][:10]
                                 + ' ' + session['end_date'][11:16])
                click_sessions[click_session] = room
        else:
            print(f'{Fore.RED}|', end='', flush=True)
    print()
    return click_sessions


def click_export_registered(click_rooms):
    '''
    Returns ClickMeeting room registrations within chosen time range
    '''

    sessions_to_import = {}

    # Calls registrations API only if room has active registration
    for room in click_rooms:
        room_id = room[0]
        room_name = room[1]
        root = f'{click_root}conferences/{room_id}/registrations/all'
        response = api_request(root, eloqua_auth=eloqua_key, api='click')
        if response.status_code == 200:
            print(f'\n{Fore.YELLOW}» {root} '
                  f'{Fore.GREEN}({response.status_code})')
            registered = response.json()

            if response:
                # Create list of registered
                registered_list = []
                for user in registered:
                    if user['fields']['Email Address'] is not None:
                        registered_list.append(user['fields']['Email Address'])

                # Deduplicating list of email addresses
                registered_list = list(set(registered_list))

# <Company specific code> =========================================================================
                # Filter out corporate and spam e-mails
                registered_list = [user for user in registered_list if
                                   '@wolterskluwer.' not in user.lower() and len(user) > 8]

                # Modifying values for Eloqua naming convention
                room_name = room_name.replace(',', '').replace(
                    '!', '').replace('-', '').replace('.', '').replace(
                        ':', '').replace('?', '').replace('–', '').replace(' ', '-')
                room_name = room_name[:26] + '-' if len(room_name) > 26 \
                    else room_name + '-'
                psp_name = naming[source_country]['webinar']['progman_psp'] if 'Progman' in room_name else naming[source_country]['webinar']['webinar_psp']

                # Naming convention for shared list of uploaded registered users
                shared_list_name = naming[source_country]['webinar']['name'] + room_name + psp_name + '_zarejestrowani'
                while '--' in shared_list_name:
                    shared_list_name = shared_list_name.replace('--', '-')
# ========================================================================= </Company specific code>

                # Create dict with name and email list
                sessions_to_import[shared_list_name] = registered_list
                print(f'\t{Fore.GREEN}{shared_list_name}')
        else:
            print(f'{Fore.RED}|', end='', flush=True)

    # Cleans pairs with empty value from import
    sessions_to_import = {k: v for (k, v) in sessions_to_import.items() if v}

    return sessions_to_import  # {'listName': ['mail', 'mail']}


def click_export_attendees(click_sessions, export_time_range):
    '''
    Returns ClickMeeting attendees from sessions within chosen time range
    '''

    sessions_to_import = {}

    # Create list of attendees of each session in choosen period
    for key, value in click_sessions.items():
        # click_sessions unpacking
        session_id, session_date = key
        room_id, room_name = value

        # Creating datetime version of session_date for EXPORT_TIME_RANGE
        session_datetime = datetime.datetime.strptime(
            session_date, '%Y-%m-%d %H:%M')

        # Calls attendees API only if session within given time range
        if (datetime.datetime.today() - session_datetime).days <= export_time_range:
            root = f'{click_root}conferences/{room_id}/sessions/{session_id}/attendees'
            response = api_request(root, eloqua_auth=eloqua_key, api='click')
            attendees = response.json()

            # Create list of attendees
            attendees_list = []
            for attendee in attendees:
                if attendee['role'] == 'listener' and attendee['email'] is not None:
                    attendees_list.append(attendee['email'])

            # Deduplicating list of email addresses
            attendees_list = list(set(attendees_list))

# <Company specific code> =========================================================================
            # Filter out corporate and spam e-mails
            attendees_list = [att for att in attendees_list if
                              '@wolterskluwer.' not in att.lower() and len(att) > 8]

            # Modifying values for Eloqua naming convention
            room_name = room_name.replace(',', '').replace(
                '!', '').replace('-', '').replace('.', '').replace(
                    ':', '').replace('?', '').replace('–', '').replace(' ', '-')
            room_name = room_name[:29] + '-' if len(room_name) > 29 \
                else room_name + '-'
            session_date = f'{session_date[8:10]}-{session_date[5:7]}-{session_date[2:4]}-'
            psp_name = naming[source_country]['webinar']['progman_psp'] if 'Progman' in room_name else naming[source_country]['webinar']['webinar_psp']

            # Naming convention for shared list of uploaded attendees
            shared_list_name = naming[source_country]['webinar']['name'] + room_name + \
                session_date + psp_name + '_uczestnicy'
            while '--' in shared_list_name:
                shared_list_name = shared_list_name.replace('--', '-')
# ========================================================================= </Company specific code>

            # Create dict with name and email list
            sessions_to_import[shared_list_name] = attendees_list
            print(f'\t{Fore.GREEN}{shared_list_name}')

    return sessions_to_import  # {'listName': ['mail', 'mail']}


'''
=================================================================================
                            Eloqua API specific functions
=================================================================================
'''


def eloqua_create_sharedlist(export):
    '''
    Creates shared list for contacts
    Requires 'export' dict with webinars and conctacts in format:
    {'listName': ['mail', 'mail']}
    '''
    outcome = []
    print(f'\n{Fore.BLUE}Saving to WK{source_country} - Webinars')

    # Unpacks export
    for name, contacts in export.items():
        root = f'{eloqua_rest}assets/contact/list'
        data = {'name': f'{name}',
                'description': 'Webinar API Upload',
                'folderId': f'{shared_list}'}
        response = api_request(
            root, eloqua_auth=eloqua_key, call='post', data=json.dumps(data))
        sharedlist = response.json()

        # Simple shared list creation
        if response.status_code == 201:
            print(f'{Fore.YELLOW}» {root} '
                  f'{Fore.GREEN}({response.status_code})')
            print(f'\t{Fore.YELLOW}{name} '
                  f'{Fore.GREEN}[Created]')
            list_id = int(sharedlist['id'])

        # Shared list already exists - appending data
        else:
            print(f'{Fore.YELLOW}» {root} '
                  f'{Fore.RED}({response.status_code})')
            print(f'\t{Fore.YELLOW}{name} '
                  f'{Fore.RED}[Exists]{Fore.GREEN} » [Append]')
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
    response = api_request(
        root, eloqua_auth=eloqua_key, call='post', data=json.dumps(data))
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
    api_request(root, eloqua_auth=eloqua_key, call='post', data=json.dumps(upload))

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
    response = api_request(
        root, eloqua_auth=eloqua_key, call='post', data=json.dumps(sync_body))
    sync_eloqua = response.json()

    # Checks stats of sync
    sync_uri = sync_eloqua['uri']
    status = sync_eloqua['status']
    while status != 'success':
        root = eloqua_bulk + sync_uri
        sync_body = {'syncedInstanceUri': f'/{sync_uri}'}
        response = api_request(root, eloqua_auth=eloqua_key)
        sync_status = response.json()
        status = sync_status['status']
        print(f'{Fore.BLUE}{status}/', end='', flush=True)
        if status == 'warning' or status == 'error':
            logs = eloqua_log_sync(uri)
            print(logs)
            break
        time.sleep(1)
    print(f'\n{Fore.YELLOW}» {root} '
          f'{Fore.GREEN}({response.status_code})\n')

    return status


def eloqua_log_sync(uri):
    '''
    Shows log for problematic sync
    Requires uri key to get id of sync
    Returns logs of sync
    '''
    id = uri[-5:]
    root = eloqua_bulk + f'syncs/{id}/logs'
    response = api_request(root, eloqua_auth=eloqua_key)
    logs_eloqua = response.json()

    return logs_eloqua


'''
=================================================================================
                                Main program flow
=================================================================================
'''

def click_to_elq(country, click_auth, eloqua_auth, eloqua_root):
    '''
    Gets attendees and users registered to ClickMeeting webinars 
    and uploads them to Eloqua as a shared list
    '''

    # Gets data from naming.json
    with open(file('naming'), 'r', encoding='utf-8') as f:
        global naming
        naming = json.load(f)

    # Creates global source_country from main module
    global source_country
    source_country = country

    # Creates globals related to Eloqua API
    global eloqua_key
    eloqua_key = eloqua_auth
    global eloqua_bulk
    eloqua_bulk = eloqua_root + '/api/BULK/2.0/'
    global eloqua_rest
    eloqua_rest = eloqua_root + '/api/REST/1.0/'

    # Creates globals related to Click API
    global click_key
    click_key = click_auth
    global click_root
    click_root = 'https://api.clickmeeting.com/v1/'

    # Creates global shared_list information from json
    global shared_list
    shared_list = naming['PL']['webinar']['sharedlist']

    # Gets export time frame from user
    while True:
        print(f'{Fore.YELLOW}Enter number of days to export:', end='')
        export_time_range = input(' ')
        try:
            export_time_range = int(export_time_range)
        except ValueError:
            print(f'\t{Fore.RED}[ERROR] {Fore.YELLOW}Please enter numeric value!')
            continue
        else:
            break
    
    # Function pipe
    click_rooms = click_export_rooms()
    click_sessions = click_export_sessions(click_rooms)
    click_registered_export = click_export_registered(click_rooms)
    click_attendee_export = click_export_attendees(click_sessions, export_time_range)
    click_exports = {**click_registered_export, **click_attendee_export}
    click_exports = {k: v for (k, v) in click_exports.items() if len(v) != 0}
    eloqua_sharedlist = eloqua_create_sharedlist(click_exports)
    print(f'\n{Fore.BLUE}Contact uploads:')
    for export in eloqua_sharedlist:
        print(
            f'{Fore.YELLOW}[{export[0]}] {Fore.GREEN}{export[1]}'
            f' - {Fore.BLUE}{export[2]} contacts {Fore.YELLOW}({export[3]})')

'''
TODO:
- Optimization of time and numer of API calls
- Save already sent, one time rooms to not overwrite each time 
'''