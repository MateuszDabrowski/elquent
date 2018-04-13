#!/usr/bin/env python3.6
# -*- coding: utf8 -*-

'''
ELQuent.webinar
Gets attendees and registered users from ClickMeeting
and uploads them to Oracle Eloqua as shared list

Mateusz Dąbrowski
github.com/MateuszDabrowski
linkedin.com/in/mateusz-dabrowski-marketing/
'''

# Python imports
import os
import sys
import json
import pickle
import datetime
import requests
import encodings
import pyperclip
from colorama import Fore, init

# ELQuent imports
import utils.api.api as api

# Initialize colorama
init(autoreset=True)


'''
=================================================================================
                            File Path Getter
=================================================================================
'''


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
        elif dir == 'api':  # For writing auth files
            if getattr(sys, 'frozen', False):
                datadir = os.path.dirname(sys.executable)
            else:
                datadir = os.path.dirname(os.path.dirname(__file__))
            return os.path.join(datadir, 'utils', dir, filename)

    file_paths = {
        'naming': find_data_file('naming.json', dir='api'),
        'click': find_data_file('click.p', dir='api')
    }

    return file_paths.get(file_path)


'''
=================================================================================
                                Click Authentication
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


'''
=================================================================================
                        ClickMeeting API specific functions
=================================================================================
'''


def click_export_rooms(export_time_range):
    '''
    Returns tuples of active and inactive ClickMeeting rooms with ID and name
    '''

    # Save active rooms
    active_ids = []
    active_names = []
    root = click_root + 'conferences/active'
    response = api.api_request(root, api='click')
    rooms_active_click = response.json()
    for room in rooms_active_click:
        active_ids.append(room['id'])
        active_names.append(room['name'])
    active_rooms = list(zip(active_ids, active_names))

    # Save inactive rooms
    inactive_ids = []
    inactive_names = []
    root = click_root + 'conferences/inactive'
    response = api.api_request(root, api='click')
    rooms_inactive_click = response.json()
    for room in rooms_inactive_click:
        # Creating datetime version of room end date
        room_date = room['ends_at'][:10] + ' ' + room['ends_at'][11:16]
        room_datetime = datetime.datetime.strptime(room_date, '%Y-%m-%d %H:%M')
        # Exporting room only if end date withing export date time
        if (datetime.datetime.today() - room_datetime).days <= export_time_range:
            inactive_ids.append(room['id'])
            inactive_names.append(room['name'])
    inactive_rooms = list(zip(inactive_ids, inactive_names))

# <Company specific code> =========================================================================
    # Filter out internal webinars from export
    internal_webinars = naming[source_country]['webinar']['filters']
    for filtering in internal_webinars:
        active_rooms = [(id, name) for (id, name)
                        in active_rooms if f'{filtering}' not in name.lower()]
        inactive_rooms = [(id, name) for (id, name)
                          in inactive_rooms if f'{filtering}' not in name.lower()]
# ========================================================================= </Company specific code>

    return (active_rooms, inactive_rooms)


def click_export_sessions(click_rooms):
    '''
    Returns ClickMeeting sessions for active and inactive rooms
    '''

    click_sessions = {}

    # Save all sessions
    for room in click_rooms:
        root = f'{click_root}conferences/{room[0]}/sessions'
        response = api.api_request(root, api='click')
        if response.status_code == 200:
            print(f'{Fore.GREEN}|', end='', flush=True)
            sessions_in_room = response.json()
            for session in sessions_in_room:
                click_session = (session['id'], session['end_date'][: 10]
                                 + ' ' + session['end_date'][11:16])
                click_sessions[click_session] = room
        else:
            print(f'{Fore.RED}|', end='', flush=True)
    print()
    return click_sessions


def click_export_registered(active_rooms):
    '''
    Returns ClickMeeting room registrations within chosen time range
    '''

    sessions_to_import = {}

    # Calls registrations API only if room has active registration
    for room in active_rooms:
        room_id = room[0]
        room_name = room[1]
        root = f'{click_root}conferences/{room_id}/registrations/all'
        response = api.api_request(root, api='click')
        if response.status_code == 200:
            print(f'{Fore.GREEN}|', end='', flush=True)
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
                shared_list_name = naming[source_country]['webinar']['name'] + \
                    room_name + psp_name + '_zarejestrowani'
                while '--' in shared_list_name:
                    shared_list_name = shared_list_name.replace('--', '-')
# ========================================================================= </Company specific code>

                # Create dict with name and email list
                sessions_to_import[shared_list_name] = registered_list
        else:
            print(f'{Fore.RED}|', end='', flush=True)

    # Cleans pairs with empty value from import
    sessions_to_import = {
        k: v for (k, v) in sessions_to_import.items() if len(v) != 0}
    print()
    for name, mails in sessions_to_import.items():
        print(
            f'{Fore.WHITE}[{Fore.YELLOW}{len(mails)}{Fore.WHITE}] {name}')

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
            response = api.api_request(
                root, api='click')
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

    # Cleans pairs with empty value from import
    sessions_to_import = {
        k: v for (k, v) in sessions_to_import.items() if len(v) != 0}
    for name, mails in sessions_to_import.items():
        print(
            f'{Fore.WHITE}[{Fore.YELLOW}{len(mails)}{Fore.WHITE}] {name}')

    return sessions_to_import  # {'listName': ['mail', 'mail']}


'''
=================================================================================
                                Main program flow
=================================================================================
'''


def click_to_elq(country):
    '''
    Gets attendees and users registered to ClickMeeting webinars 
    and uploads them to Eloqua as a shared list
    '''
    # Gets required auths
    click_auth = get_click_auth()

    # Gets data from naming.json
    with open(file('naming'), 'r', encoding='utf-8') as f:
        global naming
        naming = json.load(f)

    # Creates global source_country from main module
    global source_country
    source_country = country

    # Creates globals related to Click API
    global click_key
    click_key = click_auth
    global click_root
    click_root = 'https://api.clickmeeting.com/v1/'

    # Gets export timeframe from user
    while True:
        print(
            f'\n{Fore.WHITE}» [{Fore.YELLOW}TIMEFRAME{Fore.WHITE}] Enter number of days to export:', end='')
        export_time_range = input(' ')
        try:
            export_time_range = int(export_time_range)
        except ValueError:
            print(
                f'\t{Fore.RED}[ERROR] {Fore.YELLOW}Please enter numeric value!')
            continue
        else:
            break

    # Function pipe
    print(f'\n{Fore.YELLOW}» Getting rooms from chosen timeframe')
    active_rooms, inactive_rooms = click_export_rooms(export_time_range)
    print(f'{Fore.GREEN}» Imported {len(active_rooms)} active and {len(inactive_rooms)} inactive rooms')
    click_rooms = active_rooms + inactive_rooms
    print(f'\n{Fore.YELLOW}» Getting sessions')
    click_sessions = click_export_sessions(click_rooms)
    print(f'{Fore.GREEN}» Imported {len(click_sessions)} sessions')
    print(f'\n{Fore.YELLOW}» Getting registered users in active rooms')
    click_registered_export = click_export_registered(active_rooms)
    print(f'{Fore.GREEN}» Imported registed users from {len(click_registered_export)} webinars')
    print(f'\n{Fore.YELLOW}» Getting attendees from choosen timeframe')
    click_attendee_export = click_export_attendees(
        click_sessions, export_time_range)
    print(f'{Fore.GREEN}» Imported attendees from {len(click_attendee_export)} webinars')
    click_exports = {**click_registered_export, **click_attendee_export}
    api.upload_contacts(source_country, click_exports, 'webinar', 'append')

    print(f'\n{Fore.GREEN}-----------------------------------------------------------------------------')

    return True
