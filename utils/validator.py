#!/usr/bin/env python3.6
# -*- coding: utf8 -*-

'''
ELQuent.validator
ELQuent campaign and asset validator

Mateusz Dąbrowski
github.com/MateuszDabrowski
linkedin.com/in/mateusz-dabrowski-marketing/
'''

# Python imports
import os
import sys
import csv
import json
import webbrowser
from datetime import datetime
from colorama import Fore, Style, init

# ELQuent imports
import utils.helper as helper
import utils.api.api as api

# Initialize colorama
init(autoreset=True)

# Globals
naming = None
source_country = None
campaign_name = None
campaign_name_base = None
search_query = None
validation_errors = None

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

    # Prepares globals for imported modules
    helper.country_naming_setter(source_country)

    # Loads json file with naming convention
    with open(file('naming'), 'r', encoding='utf-8') as f:
        global naming
        naming = json.load(f)


'''
=================================================================================
                            File Path Getter
=================================================================================
'''


def file(file_path, name=''):
    '''
    Returns file path to template files
    '''

    def find_data_file(filename, directory='templates'):
        '''
        Returns correct file path for both script and frozen app
        '''
        if directory == 'templates':  # For reading template files
            if getattr(sys, 'frozen', False):
                datadir = os.path.dirname(sys.executable)
            else:
                datadir = os.path.dirname(os.path.dirname(__file__))
            return os.path.join(datadir, 'utils', directory, filename)
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
        'email-groups': find_data_file(f'WKCORP_email-groups.json'),
        'outcome-csv': find_data_file(f'WK{source_country}_{name}.csv', directory='outcomes')
    }

    return file_paths.get(file_path)


'''
=================================================================================
                            Campaign Asset Validation
=================================================================================
'''


def campaign_field_validator(campaign_data):
    '''
    Lists errors with campaign fields
    '''
    for field in ['Region', 'Type', 'PSP', 'VSP']:
        if not campaign_data.get(field):
            print(f'{ERROR}Campaign field {field} is not filled!')
            validation_errors.append([
                field,
                '',
                '',
                'Campaign field not filled'
            ])
        elif campaign_data.get(field) not in campaign_name:
            print(f'{ERROR}Campaign field {field} has incorrect value!')
            validation_errors.append([
                field,
                '',
                campaign_data.get(field),
                'Campaign field has incorrect value'
            ])

    return


def campaign_asset_validator(campaign_json, asset_type):
    '''
    Requires json with campaign data and asset type
    Possible asset names ['segment', 'email', 'landingPage', 'form']
    Returns a list of IDs of the assets
    '''
    asset_list = []
    asset_type_capitalized = asset_type[:1].capitalize() + asset_type[1:]
    for element in campaign_json['elements']:
        if element['type'] == f'Campaign{asset_type_capitalized}':
            # Gathers basic data on asset
            asset_list.append(element.get(f'{asset_type}Id'))

            # Validates whether there are defined outputs
            if not element.get('outputTerminals') and\
                    campaign_json['campaignCategory'] == 'multistep':
                print(f'{WARNING}{element.get("name")} '
                      f'{Fore.YELLOW}» no output routes!')
                validation_errors.append([
                    element.get('name'),
                    element.get(f'{asset_type}Id'),
                    '',
                    'No output routes on canvas'
                ])

    return asset_list


def campaign_decision_validator(campaign_data, campaign_json, decision_type):
    '''
    Requires json with campaign data and decision type
    Possible asset names ['EmailOpened', 'EmailClickthrough', 'EmailSent',
    'SubmitForm', 'ContactFilterMembershi', 'ContactListMembership']
    Returns a list of IDs of the decisions
    '''
    decision_list = []
    for element in campaign_json['elements']:
        if element['type'] == f'Campaign{decision_type}Rule':
            # Gathers basic data on decision
            if 'email' in decision_type.lower():
                decision_list.append(element.get('emailId'))
            elif 'form' in decision_type.lower():
                decision_list.append(element.get('formId'))
            elif 'filter' in decision_type.lower():
                decision_list.append(element.get('filterId'))
            elif 'list' in decision_type.lower():
                decision_list.append(element.get('listId'))

            # Validates whether decision step is set to asset from that campaign
            if decision_type in ['EmailOpened', 'EmailClickthrough', 'EmailSent']\
                    and decision_list[-1] not in campaign_data['Email']:
                connected_asset_name, _ = api.eloqua_asset_get(
                    decision_list[-1], 'email', depth='minimal')
                if campaign_name_base not in connected_asset_name:
                    print(f'{WARNING}{element.get("name")} ',
                          f'{Fore.YELLOW}» asset not used in this camapign.')
                    validation_errors.append([
                        element.get('name'),
                        decision_list[-1],
                        '',
                        'Connected to asset from different campaign'
                    ])
            elif decision_type is 'SubmitForm'\
                    and decision_list[-1] not in campaign_data['Form']:
                connected_asset_name, _ = api.eloqua_asset_get(
                    decision_list[-1], 'form', depth='minimal')
                if campaign_name_base not in connected_asset_name:
                    print(f'{WARNING}{element.get("name")} ',
                          f'{Fore.YELLOW}» asset not used in this camapign.')
                    validation_errors.append([
                        element.get('name'),
                        decision_list[-1],
                        '',
                        'Connected to asset from different campaign'
                    ])

            # Validates whether there are defined outputs
            if not element.get('outputTerminals'):
                print(f'{ERROR}{element.get("name")} '
                      f'{Fore.YELLOW}» no output routes!')
                validation_errors.append([
                    element.get('name'),
                    decision_list[-1],
                    '',
                    'No output routes on canvas'
                ])
            elif len(element['outputTerminals']) == 1:
                print(
                    f'{WARNING}{element.get("name")} '
                    f'{Fore.YELLOW}» only one output route.')
                validation_errors.append([
                    element.get('name'),
                    decision_list[-1],
                    '',
                    'Only one output route on canvas'
                ])

            # Validates whether there is correct evaluation period
            if element.get('evaluateNoAfter') == '0':
                print(f'{ERROR}{element.get("name")} '
                      f'{Fore.RED}There is no evaluation period.')
                validation_errors.append([
                    element.get('name'),
                    decision_list[-1],
                    '',
                    'There is no evaluation period set'
                ])

    return decision_list


def campaign_email_validator(email_json_list):
    '''
    Requires list with e-mail jsons from API response
    '''
    email_id_list = []
    # Iterate over all e-mails connected with campaign
    for email in email_json_list:
        # Adds e-mail ID to email_id_list
        email_id_list.append(email.get('id'))

        # TODO: e-mail validation logic

    return email_id_list


def campaign_data_getter():
    '''
    Automatically tests whether campaign assets are correct
    Currently checks:
    » Canvas:
        › Campaign Fields (completness and correctness)
        › Asset Steps (output routes)
        › Decision Steps (attribution, evaluation and output routes)
    '''
    # Gets name of the campaign that should be validated
    global campaign_name
    global campaign_name_base
    campaign_name = helper.campaign_name_getter()
    campaign_name_base = '_'.join(campaign_name[:-1])
    campaign_name = '_'.join(campaign_name)

    # Creates list to group all errors and warnings ['Name','ID','Value','ErrorDescription']
    global validation_errors
    validation_errors = []

    # Searches Eloqua for a campaign with above acquired name
    campaign_json = api.eloqua_get_assets(campaign_name, asset_type='campaign')
    if len(campaign_json['elements']) > 1:
        print(f'{ERROR}There is more than one campaign with the same name!')
        return False
    else:
        campaign_json = campaign_json['elements'][0]

    # Creates dict to map information about the campaign
    print(f'\n{Fore.WHITE}» Campaign Validation')
    campaign_data = {
        'Name': campaign_json['name'],
        'ID': campaign_json['id'],
        'Category': 'multistep' if campaign_json['campaignCategory'] == 'contact' else 'simple',
        'StartDate': helper.epoch_to_date(campaign_json.get('startAt', False)),
        'EndDate': helper.epoch_to_date(campaign_json.get('endAt', False)),
        'Region': campaign_json.get('region'),
        'Type': campaign_json.get('campaignType'),
        'PSP': campaign_json['fieldValues'][0].get('value'),
        'VSP': campaign_json.get('product'),
    }

    # Validate campaign fields
    campaign_field_validator(campaign_data)

    # Validate all assets included in the campaign and add to campaign_data
    for asset in ['segment', 'email', 'landingPage', 'form']:
        asset_id_list = campaign_asset_validator(campaign_json, asset)
        asset_capitalized = asset[:1].capitalize() + asset[1:]
        campaign_data[asset_capitalized] = asset_id_list

    # Validate all decision steps in the campaign
    for decision in ['EmailOpened', 'EmailClickthrough', 'EmailSent', 'SubmitForm',
                     'ContactFilterMembershi', 'ContactListMembership']:
        decision_id_list = campaign_decision_validator(
            campaign_data, campaign_json, decision)
        campaign_data[decision] = decision_id_list

    # Building search query to find assets connected with campaign
    global search_query
    search_query = campaign_name.split('_')
    search_query = ('_').join(search_query[0:-1]) + '*'

    # Create dict containing full data on all assets conencted with campaign
    all_campaign_assets = {}
    for asset_type in ['segment', 'email', 'landingPage', 'form']:
        page = 1
        assets = []
        while True:
            # Gets full data on first part of assets connected with campaign
            assets_partial = api.eloqua_get_assets(
                search_query, asset_type, page=page)

            # Stop if there is none of particular asset_type
            if not assets_partial:
                print(
                    f'{Fore.WHITE}[{Fore.YELLOW}{asset}{Fore.WHITE}] » '
                    f'{Fore.YELLOW}Not found for {campaign_name}')
                break

            # Add existing to a list
            for single_asset in assets_partial['elements']:
                assets.append(single_asset)

            # Stops iteration when full list is obtained
            if assets_partial['total'] - page * 20 < 0:
                break

            # Else increments page to get next part of outcomes
            page += 1

            # Every ten batches draws hyphen for better readability
            if page % 10 == 0:
                print(f'{Fore.YELLOW}-', end='', flush=True)

        # Add all assets to all_campaign_assets dict
        all_campaign_assets[asset_type] = assets

    print(f'\n{Fore.RED}» Errors:')
    for error in validation_errors:
        print(error)

    # TODO: Validate campaign elements
    # TODO: Validate names of all assets
    # TODO: Validate tracking and PURLs in e-mails
    # TODO: Validate implementation of forms on LP's (especially e-mail validation and field merges)
    # TODO: Automatically fix all bugs using APIs

    return


'''
=================================================================================
                            Campaign Lifespan Validation
=================================================================================
'''


def lifespan_analytics_menu(today):
    '''
    Automatically points at campaigns that require attention and allows to take action
    '''

    def lifespan_analytics(campaign_list):
        '''
        Shows chosen list of attention needing campaigns and allows to open them in Eloqua for further analysis
        campaign_list is a list of lists with ['id', 'name', 'createdBy', 'lifespan']
        '''
        for campaign in campaign_list:
            print(
                f'\n{Fore.YELLOW}» {Fore.WHITE}{campaign[1]}'
                f'\n{Fore.WHITE}[Span: {Fore.YELLOW}{campaign[3]} days{Fore.WHITE}] '
                f'{Fore.WHITE}[ID: {Fore.YELLOW}{campaign[0]}{Fore.WHITE}] '
                f'{Fore.WHITE}[User: {Fore.YELLOW}{campaign[2]}{Fore.WHITE}]')

        print(f'\n{Fore.YELLOW}» Open all those campaigns in Eloqua? '
              f'{Fore.WHITE}({YES}/{NO}):', end='')
        choice = input(' ')
        if choice.lower() == 'y':
            for campaign in campaign_list:
                # Open in new tab
                url = naming['root'] + '#campaigns&id=' + campaign[0]
                webbrowser.open(url, new=2, autoraise=True)

        return

    # Lists of attention needing campaigns
    over_10_prof = []
    over_90 = []
    over_365 = []

    # Builds lists with data from campaign-lifespan function
    with open(file('outcome-csv', f'active-campaigns-{today}'), 'r', encoding='utf-8') as f:
        export_reader = csv.reader(f)
        next(f)  # Skips header row
        # Each row is campaign data ['Name', 'ID', 'CreatedBy', 'CreatedAt', 'UpdatedAt', 'StartAt', 'EndAt', 'Members']
        for row in export_reader:
            delta = datetime.strptime(row[6], '%Y-%m-%d')\
                - datetime.strptime(row[5], '%Y-%m-%d')
            if 'WKPL_PROF_BOO' in row[0] and delta.days > 10:
                over_10_prof.append([row[1], row[0], row[2], delta.days])
            if delta.days > 90:
                over_90.append([row[1], row[0], row[2], delta.days])
            if delta.days > 365:
                over_365.append([row[1], row[0], row[2], delta.days])

    # Exits module if nothing requires attention
    if not over_10_prof and not over_90 and not over_365:
        print(f'{SUCCESS}No campaign end date requiring attention')
        return

    # Sorts lists by campaign lifespan
    over_10_prof = sorted(over_10_prof, key=lambda item: item[3], reverse=True)
    over_90 = sorted(over_90, key=lambda item: item[3], reverse=True)
    over_365 = sorted(over_365, key=lambda item: item[3], reverse=True)

    # Shows user outcome of analysis and allows him to dive deeper
    while True:
        print(f'\n{Fore.GREEN}Show:')
        # Analysis menu
        if over_10_prof and source_country == 'PL':
            print(
                f'{Fore.WHITE}[{Fore.YELLOW}0{Fore.WHITE}]\t» {Fore.YELLOW}{len(over_10_prof)} '
                f'{Fore.WHITE}Profinfo campaigns set for longer than {Fore.YELLOW}10{Fore.WHITE} days')
        if over_90:
            print(
                f'{Fore.WHITE}[{Fore.YELLOW}1{Fore.WHITE}]\t» {Fore.YELLOW}{len(over_90)} '
                f'{Fore.WHITE}campaigns set for longer than {Fore.YELLOW}90{Fore.WHITE} days')
        if over_365:
            print(
                f'{Fore.WHITE}[{Fore.YELLOW}2{Fore.WHITE}]\t» {Fore.YELLOW}{len(over_365)} '
                f'{Fore.WHITE}campaigns set for longer than {Fore.YELLOW}365{Fore.WHITE} days')
        print(
            f'{Fore.WHITE}[{Fore.YELLOW}Q{Fore.WHITE}]\t» [{Fore.YELLOW}Quit to main menu{Fore.WHITE}]')

        print(
            f'{Fore.GREEN}Enter number associated with chosen option:', end='')
        choice = input(' ')
        if choice.lower() == 'q':
            break
        elif choice == '0':
            print(f'\n{Fore.YELLOW}Profinfo Campaigns spanning over 10 days:')
            lifespan_analytics(over_10_prof)
        elif choice == '1':
            print(f'\n{Fore.YELLOW}Campaigns spanning over 90 days:')
            lifespan_analytics(over_90)
        elif choice == '2':
            print(f'\n{Fore.YELLOW}Campaigns spanning over a year:')
            lifespan_analytics(over_365)
        else:
            print(f'{Fore.RED}Entered value does not belong to any option!')
            choice = ''

    return


def campaign_lifespan():
    '''
    Creates report containg all active campaigns with end date after chosen period
    '''
    # Creates list to store all active multistep campaigns
    active_campaigns = []

    '''
    =================================================== Gets IDs of all active multistep campaigns
    '''

    # Builds search query for API
    campaign_query = f"name='WK{source_country}*'"

    # Iterates over pages of outcomes
    page = 1
    print(f'\n{Fore.WHITE}[{Fore.YELLOW}SYNC{Fore.WHITE}] ',
          end='', flush=True)
    while True:
        campaigns = api.eloqua_get_assets(
            campaign_query, asset_type='campaign', page=page, depth='minimal')

        # Adds active campaigns to a list
        for campaign in campaigns['elements']:
            if campaign['currentStatus'] == 'Active' and campaign['isEmailMarketingCampaign'] == 'false':
                active_campaigns.append(int(campaign['id']))

        # Stops iteration when full list is obtained
        if campaigns['total'] - page * 500 < 0:
            break

        # Else increments page to get next part of outcomes
        page += 1

        # Every ten batches draws hyphen for better readability
        if page % 10 == 0:
            print(f'{Fore.YELLOW}-', end='', flush=True)
    print(f'\n{SUCCESS}Exported all {len(active_campaigns)} active multistep campaigns for WK{source_country}')

    '''
    =================================================== Exports data of each active multistep campaign
    '''

    # Gets date for file naming
    today = str(datetime.now())[:10]

    # Dict of users for id to name swap
    user_dict = {}

    # Creates file to save outcomes
    with open(file('outcome-csv', f'active-campaigns-{today}'), 'w', encoding='utf-8') as f:
        fieldnames = ['Name', 'ID', 'CreatedBy', 'CreatedAt', 'UpdatedAt',
                      'StartAt', 'EndAt', 'Members']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

    # Gets data on each active multistep campaign
    print(f'\n{Fore.WHITE}[{Fore.YELLOW}SYNC{Fore.WHITE}] ',
          end='', flush=True)
    for campaign_id in active_campaigns:
        campaign = api.eloqua_asset_get(
            campaign_id, asset_type='campaign', depth='complete')

        campaign_info = {
            'Name': campaign['name'],
            'ID': int(campaign['id']),
            'CreatedAt': datetime.utcfromtimestamp(int(campaign['createdAt'])).strftime('%Y-%m-%d %H:%M:%S'),
            'UpdatedAt': datetime.utcfromtimestamp(int(campaign['updatedAt'])).strftime('%Y-%m-%d %H:%M:%S'),
            'StartAt': datetime.utcfromtimestamp(int(campaign['startAt'])).strftime('%Y-%m-%d'),
            'EndAt': datetime.utcfromtimestamp(int(campaign['endAt'])).strftime('%Y-%m-%d'),
        }

        # Gets user name with least API calls required
        try:
            campaign_info['CreatedBy'] = user_dict[campaign['createdBy']]
        except KeyError:
            user_dict[campaign['createdBy']] = helper.user_getter(
                campaign['createdBy']).get('name', campaign['createdBy'])
            campaign_info['CreatedBy'] = user_dict[campaign['createdBy']]

        # Gets member count for the campain if any
        try:
            campaign_info['Members'] = campaign['memberCount']
        except KeyError:
            campaign_info['Members'] = '0'

        # Append batch of data to file
        with open(file('outcome-csv', f'active-campaigns-{today}'), 'a', encoding='utf-8') as f:
            fieldnames = ['Name', 'ID', 'CreatedBy', 'CreatedAt', 'UpdatedAt',
                          'StartAt', 'EndAt', 'Members']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writerow(campaign_info)

        # Clears dict for next batch
        campaign_info = {}

        print(f'{Fore.GREEN}|', end='', flush=True)
    print(
        f'\n{SUCCESS}Saved data of {len(active_campaigns)} campaigns to Outcomes folder')

    lifespan_analytics_menu(today)

    return


'''
=================================================================================
                            Voucher Code App Validation
=================================================================================
'''


def voucher_validation_menu():
    '''
    Gets information whether user wants to build up campaign list or validate the campaigns
    '''

    while True:
        print(
            f'\n{Fore.GREEN}ELQuent.validator Voucher Campaign Options:'
            f'\n{Fore.WHITE}[{Fore.YELLOW}1{Fore.WHITE}]\t» [{Fore.YELLOW}List{Fore.WHITE}] Show which campaigns are already in the checklist'
            f'\n{Fore.WHITE}[{Fore.YELLOW}2{Fore.WHITE}]\t» [{Fore.YELLOW}Add{Fore.WHITE}] Adds new voucher campaign to the checklist'
            f'\n{Fore.WHITE}[{Fore.YELLOW}3{Fore.WHITE}]\t» [{Fore.YELLOW}Validate{Fore.WHITE}] Validates voucher campaign stored in the checklist'
            f'\n{Fore.WHITE}[{Fore.YELLOW}Q{Fore.WHITE}]\t» [{Fore.YELLOW}Quit to main menu{Fore.WHITE}]'
        )
        print(f'{Fore.YELLOW}Enter number associated with chosen utility:', end='')
        choice = input(' ')
        if choice.lower() == 'q':
            break
        elif choice == '1':
            voucher_list_print()
        elif choice == '2':
            voucher_list_update()
        elif choice == '3':
            voucher_validation()
        else:
            print(f'{Fore.RED}Entered value does not belong to any utility!')
            choice = ''

    return


def voucher_list_print():
    '''
    Prints voucher campaign list
    '''

    # Gets list of already uploaded voucher campaigns
    uploaded_voucher_shared_list = api.eloqua_asset_get(
        naming[source_country]['id']['voucher_campaigns'], 'sharedContent', depth='complete')
    old_voucher_shared_txt = uploaded_voucher_shared_list['contentHtml']
    if old_voucher_shared_txt:
        old_voucher_shared_dict = json.loads(old_voucher_shared_txt)
    else:
        print(
            f'\n{Fore.WHITE}» {Fore.YELLOW}There is no voucher campaigns on the list')
        return False

    print(
        f'\n{Fore.GREEN}Found {Fore.WHITE}{len(old_voucher_shared_dict.keys())}{Fore.GREEN} Voucher Campaigns:')
    for element in old_voucher_shared_dict.values():
        print(
            f'{Fore.WHITE}» [ID: {Fore.YELLOW}{element["id"]}{Fore.WHITE}] '
            f'{Fore.WHITE}{element["name"]} - {Fore.YELLOW}{element["status"]}')

    return


def voucher_list_update():
    '''
    Updates voucher campaign list
    '''

    # Gets ID of campaign to be added to thje list
    while True:
        print(
            f'\n{Fore.YELLOW}Please enter ID of new campaign with the Voucher Code App:', end='')
        campaign_id = input(' ')
        if campaign_id.lower() == 'q':
            return False
        try:
            int(campaign_id)
        except (TypeError, ValueError):
            print(f'{ERROR}Please enter numeric value!')
            campaign_id = ''
            continue
        break

    # Gets list of already uploaded voucher campaigns
    uploaded_voucher_shared_list = api.eloqua_asset_get(
        naming[source_country]['id']['voucher_campaigns'], 'sharedContent', depth='complete')
    old_voucher_shared_txt = uploaded_voucher_shared_list['contentHtml']
    if old_voucher_shared_txt:
        old_voucher_shared_dict = json.loads(old_voucher_shared_txt)
    else:
        old_voucher_shared_dict = {}

    # Checks if the new ID is already in the list
    if campaign_id not in old_voucher_shared_dict.keys():
        campaign = api.eloqua_asset_get(
            campaign_id, asset_type='campaign', depth='complete')
        voucher_campaign_id = campaign['id']
        voucher_campaign_name = campaign['name']
        voucher_campaign_status = campaign['currentStatus']
        voucher_campaign_voucher_step = ''
        voucher_campaign_error_step = ''
        for element in campaign['elements']:
            if element['type'] == 'CampaignWaitAction' and element['name'] == 'Voucher Error':
                voucher_campaign_error_step = element['id']
            if element['type'] == 'CampaignCloudAction' and element['name'] == 'Code Retriever 2.0 Action Service':
                voucher_campaign_voucher_step = element['id']
            if voucher_campaign_voucher_step and voucher_campaign_error_step:
                break

        # End if there is no step with default naming convention
        if not voucher_campaign_voucher_step:
            print(
                f'\n{Fore.RED}There is no App step called "Code Retriever 2.0 Action Service" on the canvas!')
            return False
        if not voucher_campaign_error_step:
            print(
                f'\n{Fore.RED}There is no Wait step called "Voucher Error" on the canvas!')
            return False

        old_voucher_shared_dict[voucher_campaign_id] = {
            'id': voucher_campaign_id,
            'name': voucher_campaign_name,
            'status': voucher_campaign_status,
            'voucher_step': voucher_campaign_voucher_step,
            'error_step': voucher_campaign_error_step
        }

        new_voucher_shared_txt = json.dumps(old_voucher_shared_dict)

        # Build shared content data for updating the list of voucher campaigns
        data = {
            'id': uploaded_voucher_shared_list.get('id'),
            'name': uploaded_voucher_shared_list.get('name'),
            'contentHTML': new_voucher_shared_txt
        }

        # Updating list of voucher campaigns to shared content
        api.eloqua_put_sharedcontent(
            naming[source_country]['id']['voucher_campaigns'], data=data)

        print(
            f'\n{SUCCESS}Campaign {Fore.YELLOW}{voucher_campaign_name}{Fore.WHITE} added to checklist!')

        return

    # Finish process if campaign already in the dict
    else:
        print(f'\n{Fore.WHITE}» {Fore.RED}Entered campaign is already in the list!')
        return False


def voucher_validation():
    '''
    Validates voucher campaigns stored in the checklist
    '''

    return


'''
I. List building
    1. Get ID of campaign to add to a list of checked campaign
    2. Check if the given campaign has two steps - Voucher App and Voucher Error properly named
    3. Save campaign ID, name, status, and IDs of both steps as dict to shared content [#2921]

II. List validation
    1. Get dict from shared content [#2921]
    2. Check via API each step ID for time spent on it
'''

'''
=================================================================================
                                Validator module menu
=================================================================================
'''


def validator_module(country):
    '''
    Lets user choose which validator module utility he wants to use
    '''
    # Create global source_country and load json file with naming convention
    country_naming_setter(country)

    # Campaign type chooser
    print(
        f'\n{Fore.GREEN}ELQuent.validator Utilites:'
        f'\n{Fore.WHITE}[{Fore.YELLOW}1{Fore.WHITE}]\t» [{Fore.YELLOW}Lifespan{Fore.WHITE}] Exports time data of all active multistep campaigns'
        f'\n{Fore.WHITE}[{Fore.YELLOW}2{Fore.WHITE}]\t» [{Fore.YELLOW}Voucher{Fore.WHITE}] Validates voucher app in campaigns'
        # f'\n{Fore.WHITE}[{Fore.YELLOW}3{Fore.WHITE}]\t» [{Fore.YELLOW}Campaign{Fore.WHITE}] Validates various elements of chosen campaign'
        f'\n{Fore.WHITE}[{Fore.YELLOW}Q{Fore.WHITE}]\t» [{Fore.YELLOW}Quit to main menu{Fore.WHITE}]'
    )
    while True:
        print(f'{Fore.YELLOW}Enter number associated with chosen utility:', end='')
        choice = input(' ')
        if choice.lower() == 'q':
            break
        elif choice == '1':
            campaign_lifespan()
            break
        elif choice == '2':
            voucher_validation_menu()
            break
        # elif choice == '3':
        #     campaign_data_getter()
        #     break
        else:
            print(f'{Fore.RED}Entered value does not belong to any utility!')
            choice = ''

    return
