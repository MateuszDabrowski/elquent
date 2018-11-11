#!/usr/bin/env python3.6
# -*- coding: utf8 -*-

'''
ELQuent.campaign
Campaign generator utilizing other modules

Mateusz Dąbrowski
github.com/MateuszDabrowski
linkedin.com/in/mateusz-dabrowski-marketing/
'''

# Python imports
import os
import re
import sys
import json
import pyperclip
from colorama import Fore, Style, init

# ELQuent imports
import utils.api.api as api
import utils.helper as helper
import utils.page as page
import utils.mail as mail

# Initialize colorama
init(autoreset=True)

# Globals
naming = None
source_country = None
campaign_name = None
converter_choice = None
product_name = None
header_text = None
regex_asset_name = None
regex_asset_url = None
regex_product_name = None
regex_header_text = None
regex_blindform_html_name = None
regex_gtm = None

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
    page.country_naming_setter(source_country)
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


def file(file_path, name='LP'):
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
        'jquery': find_data_file('WKCORP_LP_jquery.txt'),
        'simple-campaign': find_data_file(f'WK{source_country}_CAMPAIGN_simple.json'),
        'basic-campaign': find_data_file(f'WK{source_country}_CAMPAIGN_basic.json'),
        'ebook-campaign': find_data_file(f'WK{source_country}_CAMPAIGN_ebook.json'),
        'code-campaign': find_data_file(f'WK{source_country}_CAMPAIGN_code.json'),
        'webinar-campaign': find_data_file(f'WK{source_country}_CAMPAIGN_webinar.json'),
        'asset-eml': find_data_file(f'WK{source_country}_EML_asset.txt'),
        'lp-template': find_data_file(f'WK{source_country}_LP_template.txt'),
        'ty-lp': find_data_file(f'WK{source_country}_LP_thank-you.txt'),
        'outcome-file': find_data_file(f'WK{source_country}_{name}.txt', directory='outcomes')
    }

    return file_paths.get(file_path)


'''
=================================================================================
                    CAMPAING GENERATION HELPER FUNCTIONS
=================================================================================
'''


def campaign_compile_regex():
    '''
    Creates global regex compiles for campaign flows
    '''
    global regex_asset_name
    global regex_asset_url
    global regex_product_name
    global regex_header_text
    global regex_gtm
    regex_asset_name = re.compile(r'ASSET_NAME', re.UNICODE)
    regex_asset_url = re.compile(r'ASSET_URL', re.UNICODE)
    regex_product_name = re.compile(r'PRODUCT_NAME', re.UNICODE)
    regex_header_text = re.compile(r'OPTIONAL_TEXT', re.UNICODE)
    regex_gtm = re.compile(r'<SITE_NAME>', re.UNICODE)

    return


def campaign_first_mail(main_lp_url='', mail_html='', reminder=True):
    '''
    Creates first mail and its reminder
    Returns eloqua id of both
    '''
    # Creates first mail from package
    if main_lp_url:
        mail_html = mail.mail_constructor(source_country, campaign=main_lp_url)
    elif not mail_html:  # If we don't know target URL nor have html from paste
        mail_html = mail.mail_constructor(source_country, campaign='linkless')
    if not mail_html and not reminder:
        return False
    elif not mail_html and reminder:
        return False, False

    # Create e-mail
    mail_name = (('_').join(campaign_name[0:4]) + '_EML')
    mail_id = api.eloqua_create_email(mail_name, mail_html)

    if not reminder:
        return mail_id

    regex_mail_preheader = re.compile(
        r'<!--pre-start.*?pre-end-->', re.UNICODE)
    while True:
        print(f'\n{Fore.YELLOW}»{Fore.WHITE} Write or copypaste {Fore.YELLOW}pre-header{Fore.WHITE} text for',
              f'{Fore.YELLOW}reminder{Fore.WHITE} e-mail and click [Enter]',
              f'\n{Fore.WHITE}[S]kip to keep the same pre-header as in main e-mail.')
        reminder_preheader = input(' ')
        if not reminder_preheader:
            reminder_preheader = pyperclip.paste()
            if not reminder_preheader:
                print(f'\n{ERROR}Pre-header can not be blank')
                continue
        elif len(reminder_preheader) > 140:
            print(f'\n{ERROR}Pre-header is over 140 characters long')
            continue
        else:
            break
    if reminder_preheader.lower() != 's':
        reminder_preheader = '<!--pre-start-->' + reminder_preheader + '<!--pre-end-->'
        reminder_html = regex_mail_preheader.sub(reminder_preheader, mail_html)
    else:
        reminder_html = mail_html

    # Create e-mail reminder
    reminder_name = (('_').join(campaign_name[0:4]) + '_REM-EML')
    reminder_id = api.eloqua_create_email(reminder_name, reminder_html)

    return (mail_id, reminder_id)


def campaign_main_page():
    '''
    Builds main landing page with main form in Eloqua
    Returns main LP ID and main Form ID
    '''
    print(
        f'\n{Fore.WHITE}» [{Fore.YELLOW}REQUIRED{Fore.WHITE}] Form for main LP', end='')
    file_name = (('_').join(campaign_name[1:4]) + '_LP')
    with open(file('lp-template'), 'r', encoding='utf-8') as f:
        code = f.read()
    form, required = page.create_form()
    code = page.swap_form(code, form)
    code = page.javascript(code, required)
    code = regex_product_name.sub(product_name, code)
    code = regex_header_text.sub(header_text, code)
    code = regex_gtm.sub(f'WK{source_country}_{file_name}', code)
    for i in range(len(naming[source_country]['converter']['Placeholders'])):
        placeholder = naming[source_country]['converter']['Placeholders'][i]
        regex_converter = re.compile(rf'{placeholder}', re.UNICODE)
        converter_value = naming[source_country]['converter'][converter_choice][i]
        code = regex_converter.sub(rf'{converter_value}', code)

    # Saves to Outcomes file
    print(
        f'{Fore.WHITE}» [{Fore.YELLOW}SAVING{Fore.WHITE}] WK{source_country}_{file_name}')
    with open(file('outcome-file', file_name), 'w', encoding='utf-8') as f:
        f.write(code)

    # Saves to Eloqua
    main_lp_id, _, main_lp_url = api.eloqua_create_landingpage(file_name, code)

    # Gets main form id for future campaign canvas API calls
    form_id_regex = re.compile(r'id="form(\d+?)"', re.UNICODE)
    main_form_id = form_id_regex.findall(form)[0]

    return (main_lp_id, main_lp_url, main_form_id)


def campaign_ty_page(asset_name):
    '''
    Builds one or two thank you pages after filling main form
    '''
    file_name = ('_').join(campaign_name[1:4]) + '_TY-LP'

    # Gets and prepares general TY LP structure
    with open(file('ty-lp'), 'r', encoding='utf-8') as f:
        ty_lp_code = f.read()
    ty_lp_code = regex_product_name.sub(product_name, ty_lp_code)
    ty_lp_code = regex_header_text.sub(header_text, ty_lp_code)
    ty_lp_code = regex_asset_name.sub(asset_name, ty_lp_code)
    ty_lp_code = regex_gtm.sub(f'WK{source_country}_{file_name}', ty_lp_code)

    for i in range(len(naming[source_country]['converter']['Placeholders'])):
        placeholder = naming[source_country]['converter']['Placeholders'][i]
        regex_converter = re.compile(rf'{placeholder}', re.UNICODE)
        converter_value = naming[source_country]['converter'][converter_choice][i]
        ty_lp_code = regex_converter.sub(rf'{converter_value}', ty_lp_code)

    # Saves to Outcomes file
    print(
        f'{Fore.WHITE}» [{Fore.YELLOW}SAVING{Fore.WHITE}] WK{source_country}_{file_name}')
    with open(file('outcome-file', file_name), 'w', encoding='utf-8') as f:
        f.write(ty_lp_code)

    # Saves to Eloqua
    ty_lp_id, _, _ = api.eloqua_create_landingpage(file_name, ty_lp_code)

    return ty_lp_id


def campaign_asset_mail(asset_name, asset_url):
    '''
    Creates asset e-mail in Eloqua
    Returns asset mail id
    '''
    file_name = (('_').join(campaign_name[1:4]) + '_asset-TECH-EML')
    with open(file('asset-eml'), 'r', encoding='utf-8') as f:
        asset_mail_code = f.read()
    asset_mail_code = regex_product_name.sub(product_name, asset_mail_code)
    asset_mail_code = regex_asset_name.sub(asset_name, asset_mail_code)
    asset_mail_code = regex_asset_url.sub(asset_url, asset_mail_code)
    for i in range(len(naming[source_country]['converter']['Placeholders'])):
        placeholder = naming[source_country]['converter']['Placeholders'][i]
        regex_converter = re.compile(rf'{placeholder}', re.UNICODE)
        converter_value = naming[source_country]['converter'][converter_choice][i]
        asset_mail_code = regex_converter.sub(
            rf'{converter_value}', asset_mail_code)

    # Saves to Outcomes file
    print(
        f'{Fore.WHITE}» [{Fore.YELLOW}SAVING{Fore.WHITE}] WK{source_country}_{file_name}')
    with open(file('outcome-file', file_name), 'w', encoding='utf-8') as f:
        f.write(asset_mail_code)

    # Saves to Eloqua
    asset_mail_id = api.eloqua_create_email(
        f'WK{source_country}_{file_name}', asset_mail_code)

    return asset_mail_id


'''
=================================================================================
                                SIMPLE EMAIL CAMPAIGN FLOW
=================================================================================
'''


def simple_campaign():
    '''
    Main flow for simple email campaign (no canvas)
    Creates filled up simple campaign from package
    Saves html and mjml codes of e-mail as backup to outcome folder
    '''

    # Checks if campaign is built with externally generated HTML
    alert_name = ('_').join([campaign_name[2], campaign_name[3].split('-')[0]])
    generated_mail = True if alert_name.startswith('RET_LA') else False

    # Creates main e-mail for simple campaign
    if generated_mail:
        mail_html = mail.generator_constructor(source_country)
        mail_id = campaign_first_mail(mail_html=mail_html, reminder=False)
        if not mail_id:
            return False
    else:
        mail_id = campaign_first_mail(reminder=False)
        if not mail_id:
            return False

    '''
    =================================================== Create Campaign
    '''

    # Gets campaign code out of the campaign name
    campaign_code = []
    for part in campaign_name[3].split('-'):
        if part.startswith(tuple(naming[source_country]['psp'])):
            campaign_code.append(part)
    campaign_code = '-'.join(campaign_code)

    # Loads json data for campaign canvas creation and fills it with data
    with open(file('simple-campaign'), 'r', encoding='utf-8') as f:
        campaign_json = json.load(f)
        # Change to string for easy replacing
        campaign_string = json.dumps(campaign_json)
        campaign_string = campaign_string.replace('MAIL_ID', mail_id)
        if generated_mail:
            # Create name structure for getting data from json
            generated_type = campaign_name[2] + \
                '_' + campaign_name[3].split('-')[0]
            # Capture specific folder
            folder_id = naming[source_country]['id']['campaign'].get(
                alert_name)
            # Capture specific segment
            segment_id = naming[source_country]['mail']['by_name'][generated_type]['segmentId']
            campaign_string = campaign_string.replace('SEGMENT_ID', segment_id)
        else:
            # Capture generic folder for campaign type
            folder_id = naming[source_country]['id']['campaign'].get(
                campaign_name[1])
            # Insert test segment
            campaign_string = campaign_string.replace('SEGMENT_ID', '466')
        # Change back to json for API call
        campaign_json = json.loads(campaign_string)
        campaign_json['name'] = '_'.join(campaign_name)
        campaign_json['folderId'] = folder_id
        campaign_json['region'] = campaign_name[0]
        campaign_json['campaignType'] = campaign_name[2]
        campaign_json['product'] = campaign_name[-1]
        campaign_json['fieldValues'][0]['value'] = campaign_code

    # Creates campaign with given data
    api.eloqua_create_campaign(campaign_name, campaign_json)

    '''
    =================================================== Finished :)
    '''

    print(f'\n{SUCCESS}Campaign prepared!',
          f'\n{Fore.WHITE}» Click [Enter] to continue.', end='')
    input(' ')

    return


'''
=================================================================================
                                BASIC CAMPAIGN FLOW
=================================================================================
'''


def basic_campaign():
    '''
    Main flow for basic canvas campaign (mail + reminder)
    Creates filled up campaign in Eloqua along with assets from package
    Saves html and mjml codes of e-mail as backup to outcome folder
    '''

    # Creates main e-mail and reminder
    mail_id, reminder_id = campaign_first_mail()
    if not mail_id:
        return False

    '''
    =================================================== Create Campaign
    '''

    # Chosses correct folder ID for campaign
    folder_id = naming[source_country]['id']['campaign'].get(campaign_name[1])

    # Gets campaign code out of the campaign name
    campaign_code = []
    for part in campaign_name[3].split('-'):
        if part.startswith(tuple(naming[source_country]['psp'])):
            campaign_code.append(part)
    campaign_code = '-'.join(campaign_code)

    # Loads json data for campaign canvas creation and fills it with data
    with open(file('basic-campaign'), 'r', encoding='utf-8') as f:
        campaign_json = json.load(f)
        # Change to string for easy replacing
        campaign_string = json.dumps(campaign_json)
        campaign_string = campaign_string\
            .replace('MAIL_ID', mail_id)\
            .replace('REMINDER_ID', reminder_id)
        # Change back to json for API call
        campaign_json = json.loads(campaign_string)
        campaign_json['name'] = '_'.join(campaign_name)
        campaign_json['folderId'] = folder_id
        campaign_json['region'] = campaign_name[0]
        campaign_json['campaignType'] = campaign_name[2]
        campaign_json['product'] = campaign_name[-1]
        campaign_json['fieldValues'][0]['value'] = campaign_code

    # Creates campaign with given data
    api.eloqua_create_campaign(campaign_name, campaign_json)

    '''
    =================================================== Finished :)
    '''

    print(f'\n{SUCCESS}Campaign prepared!',
          f'\n{Fore.WHITE}» Click [Enter] to continue.', end='')
    input(' ')

    return


'''
=================================================================================
                                CONTENT CAMPAIGN FLOW
=================================================================================
'''


def content_campaign():
    '''
    Main flow for e-book campaign (doi)
    Creates filled up campaign in Eloqua along with assets
    Saves multiple html codes as backup to outcome folder
    '''

    global converter_choice
    global product_name
    global header_text
    converter_choice, asset_type, asset_name = helper.asset_name_getter()
    asset_url = helper.asset_link_getter()
    product_name = helper.product_name_getter(campaign_name)
    header_text = helper.header_text_getter()

    '''
    =================================================== Builds campaign assets
    '''

    # TODO: Ask if there is external LP or eloqua one to be created
    # TODO: Ask if there is prepared Form or it needs to be created
    # Create main page with selected form
    main_lp_id, main_lp_url, main_form_id = campaign_main_page()

    # Creates main e-mail and reminder
    mail_id, reminder_id = '', ''
    print(f'\n{Fore.YELLOW}»{Fore.WHITE} Start with e-mail package? {Fore.WHITE}({YES}/{NO}):', end=' ')
    choice = input('')
    if choice.lower() == 'y':
        mail_id, reminder_id = campaign_first_mail(main_lp_url)
        if not mail_id:
            return False

    # Create one or two thank you pages depending on previous user input
    ty_page_id = campaign_ty_page(asset_name)

    # Create asset mail
    asset_mail_id = campaign_asset_mail(asset_name, asset_url)

    '''
    =================================================== Create Campaign
    '''

    # Chosses correct folder ID for campaign
    folder_id = naming[source_country]['id']['campaign'].get(campaign_name[1])

    # Gets campaign code out of the campaign name
    campaign_code = []
    for part in campaign_name[3].split('-'):
        if part.startswith(tuple(naming[source_country]['psp'])):
            campaign_code.append(part)
    campaign_code = '-'.join(campaign_code)

    # TODO: Different JSON based on whether it is e-book, recording, webinar or code
    # Loads json data for campaign canvas creation and fills it with data
    with open(file('ebook-campaign'), 'r', encoding='utf-8') as f:
        campaign_json = json.load(f)
        # Change to string for easy replacing
        campaign_string = json.dumps(campaign_json)
        campaign_string = campaign_string\
            .replace('FIRST_EMAIL', mail_id)\
            .replace('REMINDER_EMAIL', reminder_id)\
            .replace('ASSET_TYPE', asset_type)\
            .replace('ASSET_EMAIL', asset_mail_id)\
            .replace('FORM_ID', main_form_id)\
            .replace('LP_ID', main_lp_id)
        # Change back to json for API call
        campaign_json = json.loads(campaign_string)
        campaign_json['name'] = '_'.join(campaign_name)
        campaign_json['folderId'] = folder_id
        campaign_json['region'] = campaign_name[0]
        campaign_json['campaignType'] = campaign_name[2]
        campaign_json['product'] = campaign_name[-1]
        campaign_json['fieldValues'][0]['value'] = campaign_code

    # Creates campaign with given data
    api.eloqua_create_campaign(campaign_name, campaign_json)

    '''
    =================================================== Finished :)
    '''

    print(f'\n{SUCCESS}Campaign prepared!',
          f'\n{Fore.WHITE}» Click [Enter] to continue.', end='')
    input(' ')

    return


'''
=================================================================================
                                Link module menu
=================================================================================
'''


def campaign_module(country):
    '''
    Lets user choose which link module utility he wants to use
    '''
    # Create global source_country and load json file with naming convention
    country_naming_setter(country)
    global campaign_name

    # Compile necessary regex definitions
    campaign_compile_regex()

    # Campaign type chooser
    print(
        f'\n{Fore.GREEN}ELQuent.campaign Campaigns:'
        f'\n{Fore.WHITE}[{Fore.YELLOW}1{Fore.WHITE}]\t» [{Fore.YELLOW}Simple{Fore.WHITE}] Perfect for newsletters and one-offs'
        f'\n{Fore.WHITE}[{Fore.YELLOW}2{Fore.WHITE}]\t» [{Fore.YELLOW}Basic Canvas{Fore.WHITE}] When you want to send e-mail with reminder'
        f'\n{Fore.WHITE}[{Fore.YELLOW}3{Fore.WHITE}]\t» [{Fore.YELLOW}Content Canvas{Fore.WHITE}] For all campaigns with e-books, webinars, codes'
        f'\n{Fore.WHITE}[{Fore.YELLOW}Q{Fore.WHITE}]\t» [{Fore.YELLOW}Quit to main menu{Fore.WHITE}]'
    )
    while True:
        print(f'{Fore.YELLOW}Enter number associated with chosen utility:', end='')
        choice = input(' ')
        if choice.lower() == 'q':
            break
        elif choice == '1':
            campaign_name = helper.campaign_name_getter()
            simple_campaign()
            break
        elif choice == '2':
            campaign_name = helper.campaign_name_getter()
            basic_campaign()
            break
        elif choice == '3':
            campaign_name = helper.campaign_name_getter()
            content_campaign()
            break
        else:
            print(f'{Fore.RED}Entered value does not belong to any utility!')
            choice = ''

    return
