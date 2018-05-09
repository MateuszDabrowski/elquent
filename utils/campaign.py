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
import encodings
from colorama import Fore, Style, init

# ELQuent imports
import utils.api.api as api
import utils.page as page

# Initialize colorama
init(autoreset=True)

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
        elif dir == 'api':  # For reading api files
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
        'naming': find_data_file('naming.json', dir='api'),
        'jquery': find_data_file('WKCORP_jquery.txt'),
        'blindform': find_data_file(f'WK{source_country}_blindform.json'),
        'blindform-html': find_data_file(f'WK{source_country}_blindform-html.txt'),
        'blindform-css': find_data_file(f'WK{source_country}_blindform-css.txt'),
        'blindform-processing': find_data_file(f'WK{source_country}_blindform-processing.json'),
        'content-campaign': find_data_file(f'WK{source_country}_content-campaign.json'),
        'asset-eml': find_data_file(f'WK{source_country}_asset-eml.txt'),
        'confirmation-eml': find_data_file(f'WK{source_country}_confirmation-eml.txt'),
        'blank-lp': find_data_file(f'WK{source_country}_blank-lp.txt'),
        'one-column-lp': find_data_file(f'WK{source_country}_one-column-lp.txt'),
        'two-column-lp': find_data_file(f'WK{source_country}_two-column-lp.txt'),
        'ty-lp': find_data_file(f'WK{source_country}_ty-lp.txt'),
        'confirmation-lp': find_data_file(f'WK{source_country}_confirmation-lp.txt'),
        'confirmation-ty-lp': find_data_file(f'WK{source_country}_confirmation-ty-lp.txt'),
        'showhide-css': find_data_file(f'WK{source_country}_showhide-css.txt'),
        'marketing-optin': find_data_file(f'WK{source_country}_marketing-optin.txt'),
        'email-optin': find_data_file(f'WK{source_country}_email-optin.txt'),
        'phone-optin': find_data_file(f'WK{source_country}_phone-optin.txt'),
        'tracking-optin': find_data_file(f'WK{source_country}_tracking-optin.txt'),
        'gdpr-info': find_data_file(f'WK{source_country}_gdpr-info.txt'),
        'submit-button': find_data_file(f'WKCORP_submit-button.txt'),
        'validation-body': find_data_file('WKCORP_validation-body.txt'),
        'validation-element': find_data_file(f'WK{source_country}_validation-element.txt'),
        'lead-by-phone': find_data_file(f'WK{source_country}_lead-by-phone.txt'),
        'showhide-lead': find_data_file(f'WKCORP_showhide-lead.txt'),
        'conversion-lead': find_data_file(f'WK{source_country}_conversion-lead.txt'),
        'conversion-contact': find_data_file(f'WK{source_country}_conversion-contact.txt'),
        'outcome-file': find_data_file(f'WK{source_country}_{name}.txt', dir='outcomes')
    }

    return file_paths.get(file_path)


'''
=================================================================================
                                WHOLE CAMPAIGN FLOW
=================================================================================
'''


def campaign_gen(country):
    '''
    Main flow for whole campaign creations
    Saves multiple html codes to outcome folder
    '''

    # Create global source_country and load json file with naming convention
    country_naming_setter(country)
    page.country_naming_setter(country)

    # Checks if there are required source files for the source source_country
    if not os.path.exists(file('validation-element')):
        print(
            f'\t{ERROR}No template found for WK{source_country}.\n{Fore.WHITE}[Enter] to continue.', end='')
        input(' ')
        return False

    '''
    =================================================== Gather necessary informations
    '''

    # Gets campaign name from user
    while True:
        print(
            f'\n{Fore.WHITE}» [{Fore.YELLOW}CAMPAIGN{Fore.WHITE}] Write or paste name of the Campaign and click [Enter]')
        campaign_name = input(' ')
        campaign_name = campaign_name.split('_')
        if len(campaign_name) != 5:
            print(f'{ERROR}Expected 5 name elements, found {len(campaign_name)}')
        elif campaign_name[0][:2] != 'WK':
            print(f'{ERROR}"{campaign_name[0]}" is not existing country code')
        elif campaign_name[1] not in naming[source_country]['segment']:
            print(f'{ERROR}"{campaign_name[1]}" is not existing segment name')
        elif campaign_name[2] not in naming['campaign']:
            print(f'{ERROR}"{campaign_name[2]}" is not existing campaign type')
        elif campaign_name[4] not in naming['vsp']:
            print(f'{ERROR}"{campaign_name[4]}" is not existing VSP')
        else:
            break

    # Gets information about lead or not lead character of the form
    print(f'\n{Fore.GREEN}After filling the form user is:',
          f'\n{Fore.WHITE}[{Fore.YELLOW}0{Fore.WHITE}] Either lead or not (depending on submission)',
          f'\n{Fore.WHITE}[{Fore.YELLOW}1{Fore.WHITE}] Always lead',
          f'\n{Fore.WHITE}[{Fore.YELLOW}2{Fore.WHITE}] Never lead')
    while True:
        print(f'{Fore.YELLOW}Enter number associated with your choice:', end='')
        lead_or_contact_form = input(' ')
        if lead_or_contact_form in ['0', '1', '2']:
            lead_or_contact_form = int(lead_or_contact_form)
            break
        else:
            print(f'{ERROR}Entered value does not belong to any choice!')

    # Gets information about converter that is used in campaign
    print(f'\n{Fore.GREEN}After filling the form user receives:')
    converter_values = list(naming[source_country]['converter'].keys())
    for i, converter in enumerate(converter_values[2:]):
        print(
            f'{Fore.WHITE}[{Fore.YELLOW}{i}{Fore.WHITE}] {converter}')
    while True:
        print(f'{Fore.YELLOW}Enter number associated with your choice:', end='')
        converter_choice = input(' ')
        if converter_choice in ['0', '1', '2', '3', '4', '5']:
            converter_choice = converter_values[int(converter_choice) + 2]
            asset_type = converter_choice.split(' ')[0]
            print(
                f'\n{Fore.WHITE}» [{Fore.YELLOW}ASSET{Fore.WHITE}] Enter title of the {asset_type}')
            asset_name = input(' ')
            regex_asset_name = re.compile(r'ASSET_NAME', re.UNICODE)
            break
        else:
            print(f'{ERROR}Entered value does not belong to any choice!')

    # Gets link to the campaign asset
    while True:
        print(
            f'\n{Fore.WHITE}» [{Fore.YELLOW}URL{Fore.WHITE}] Enter link to the asset or asset page')
        asset_url = input(' ')
        if asset_url.startswith('http') or asset_url.startswith('www'):
            regex_asset_url = re.compile(r'ASSET_URL', re.UNICODE)
            break
        else:
            print(f'{ERROR}Entered value is not valid link!')

    # Gets product name either from campaign name or user
    local_name = campaign_name[3].split('-')
    if local_name[0] in naming[source_country]['product']:
        product_name = naming[source_country]['product'][local_name[0]]
    else:
        print(
            f'\n{Fore.WHITE}» [{Fore.YELLOW}PRODUCT{Fore.WHITE}] Could not recognize product name, please write its name: ', end='')
        product_name = input(' ')
    regex_product_name = re.compile(r'PRODUCT_NAME', re.UNICODE)

    # Gets optional text for header
    print(
        f'\n{Fore.WHITE}» [{Fore.YELLOW}OPTIONAL{Fore.WHITE}] Text to be displayed on the left side of header bar:')
    optional_text = input(' ')
    regex_optional_text = re.compile(r'OPTIONAL_TEXT', re.UNICODE)

    # Regex for GTM tag
    regex_gtm = re.compile(r'<SITE_NAME>', re.UNICODE)

    # List of created Landing Pages and E-mails:
    lp_list = []
    eml_list = []

    '''
    =================================================== Builds main page
    '''

    print(
        f'\n{Fore.WHITE}» [{Fore.YELLOW}CODE REQUIRED{Fore.WHITE}] Form on main Landing Page', end='')
    file_name = (('_').join(campaign_name[1:4]) + '_LP')
    with open(file('two-column-lp'), 'r', encoding='utf-8') as f:
        code = f.read()
    form, required = page.create_form()
    code = page.swap_form(code, form)
    code = page.javascript(code, required)
    code = regex_product_name.sub(product_name, code)
    code = regex_optional_text.sub(optional_text, code)
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
    main_lp_id = api.eloqua_create_landingpage(file_name, code)[0]
    # Saves to list of created LPs
    lp_list.append([f'WK{source_country}_{file_name}', code])

    # Gets main form id for future campaign canvas API calls
    form_id_regex = re.compile(r'id="form(\d+?)"', re.UNICODE)
    form_id = form_id_regex.findall(form)[0]

    '''
    =================================================== Builds TY-LP
    '''

    # Gets and prepares general TY LP structure
    with open(file('ty-lp'), 'r', encoding='utf-8') as f:
        code = f.read()
    code = regex_product_name.sub(product_name, code)
    code = regex_optional_text.sub(optional_text, code)

    # Lead submission TY LP
    if lead_or_contact_form == 0 or lead_or_contact_form == 1:
        file_name = (('_').join(campaign_name[1:4]) + '_lead-TY-LP')
        with open(file('conversion-lead'), 'r', encoding='utf-8') as f:
            conversion_script = f.read()
        regex_conversion_script = re.compile(r'(</body>)', re.UNICODE)
        lead_ty_lp = regex_conversion_script.sub(conversion_script, code)
        lead_ty_lp = regex_gtm.sub(
            f'WK{source_country}_{file_name}', lead_ty_lp)
        for i in range(len(naming[source_country]['converter']['Placeholders'])):
            placeholder = naming[source_country]['converter']['Placeholders'][i]
            regex_converter = re.compile(rf'{placeholder}', re.UNICODE)
            converter_value = naming[source_country]['converter'][converter_choice][i]
            lead_ty_lp = regex_converter.sub(rf'{converter_value}', lead_ty_lp)
        lead_ty_lp = lead_ty_lp\
            .replace('<!-- PRESENTATION -->', naming[source_country]['converter']['Presentation'])
        # Saves to Outcomes file
        print(
            f'{Fore.WHITE}» [{Fore.YELLOW}SAVING{Fore.WHITE}] WK{source_country}_{file_name}')
        with open(file('outcome-file', file_name), 'w', encoding='utf-8') as f:
            f.write(lead_ty_lp)
        # Saves to Eloqua
        api.eloqua_create_landingpage(file_name, lead_ty_lp)
        # Saves to list of created LPs
        lp_list.append([f'WK{source_country}_{file_name}', lead_ty_lp])

    # Not lead submission TY LP
    if lead_or_contact_form == 0 or lead_or_contact_form == 2:
        file_name = (('_').join(campaign_name[1:4]) + '_contact-TY-LP')
        with open(file('conversion-contact'), 'r', encoding='utf-8') as f:
            conversion_script = f.read()
        regex_conversion_script = re.compile(r'(</body>)', re.UNICODE)
        contact_ty_lp = regex_conversion_script.sub(conversion_script, code)
        contact_ty_lp = regex_gtm.sub(
            f'WK{source_country}_{file_name}', contact_ty_lp)
        for i in range(len(naming[source_country]['converter']['Placeholders'])):
            placeholder = naming[source_country]['converter']['Placeholders'][i]
            regex_converter = re.compile(rf'{placeholder}', re.UNICODE)
            converter_value = naming[source_country]['converter'][converter_choice][i]
            contact_ty_lp = regex_converter.sub(
                rf'{converter_value}', contact_ty_lp)
        # Saves to Outcomes file
        print(
            f'{Fore.WHITE}» [{Fore.YELLOW}SAVING{Fore.WHITE}] WK{source_country}_{file_name}')
        with open(file('outcome-file', file_name), 'w', encoding='utf-8') as f:
            f.write(contact_ty_lp)
        # Saves to Eloqua
        api.eloqua_create_landingpage(file_name, contact_ty_lp)
        # Saves to list of created LPs
        lp_list.append([f'WK{source_country}_{file_name}', contact_ty_lp])

    '''
    =================================================== Build BlindForm
    '''

    blindform_name = (('_').join(
        campaign_name[0:4]) + '_confirmation-blindFORM')
    blindform_html_name = api.eloqua_asset_html_name(blindform_name)
    regex_blindform_html_name = re.compile('HTML_FORM_NAME', re.UNICODE)

    # Loads json data for blindform creation and fills it with name and html_name
    with open(file('blindform'), 'r', encoding='utf-8') as f:
        blindform_json = json.load(f)
        blindform_json['name'] = blindform_name
        blindform_json['htmlName'] = blindform_html_name

    # Creates form with given data
    blindform_id, blindform_json = api.eloqua_create_form(
        blindform_name, blindform_json)

    # Prepares HTML Code of the form
    with open(file('blindform-html'), 'r', encoding='utf-8') as f:
        blindform_html = f.read()
        blindform_html = blindform_html\
            .replace('\\', '')\
            .replace('FORM_ID', blindform_id)\
            .replace('HTML_NAME', blindform_html_name)

    required = ''

    '''
    =================================================== Builds Confirmation-LP
    '''

    file_name = (('_').join(campaign_name[1:4]) + '_confirmation-LP')
    with open(file('confirmation-lp'), 'r', encoding='utf-8') as f:
        code = f.read()
    code = page.swap_form(code, blindform_html)
    code = page.javascript(code, required)
    code = regex_product_name.sub(product_name, code)
    code = regex_optional_text.sub(optional_text, code)
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
    api.eloqua_create_landingpage(file_name, code)
    # Saves to list of created LPs
    lp_list.append([f'WK{source_country}_{file_name}', code])

    '''
    =================================================== Builds Confirmation E-mail
    '''

    file_name = (('_').join(campaign_name[1:4]) + '_confirmation-EML')
    with open(file('confirmation-eml'), 'r', encoding='utf-8') as f:
        confirmation_code = f.read()
    confirmation_code = regex_product_name.sub(product_name, confirmation_code)
    confirmation_code = regex_asset_name.sub(asset_name, confirmation_code)
    confirmation_code = regex_blindform_html_name.sub(
        blindform_html_name, confirmation_code)
    for i in range(len(naming[source_country]['converter']['Placeholders'])):
        placeholder = naming[source_country]['converter']['Placeholders'][i]
        regex_converter = re.compile(rf'{placeholder}', re.UNICODE)
        converter_value = naming[source_country]['converter'][converter_choice][i]
        confirmation_code = regex_converter.sub(
            rf'{converter_value}', confirmation_code)
    # Saves to Outcomes file
    print(
        f'{Fore.WHITE}» [{Fore.YELLOW}SAVING{Fore.WHITE}] WK{source_country}_{file_name}')
    with open(file('outcome-file', file_name), 'w', encoding='utf-8') as f:
        f.write(confirmation_code)
    # Saves to Eloqua
    api.eloqua_create_email(
        f'WK{source_country}_{file_name}', confirmation_code)
    # Saves to list of created EMLs
    eml_list.append([f'WK{source_country}_{file_name}', confirmation_code])

    '''
    =================================================== Builds Confirmation Reminder E-mail
    '''

    file_name = (('_').join(campaign_name[1:4]) + '_confirmation-reminder-EML')
    # Saves to Outcomes file
    print(
        f'{Fore.WHITE}» [{Fore.YELLOW}SAVING{Fore.WHITE}] WK{source_country}_{file_name}')
    with open(file('outcome-file', file_name), 'w', encoding='utf-8') as f:
        f.write(confirmation_code)
    # Saves to Eloqua
    confirmation_reminder_eml_id = api.eloqua_create_email(
        f'WK{source_country}_{file_name}', confirmation_code)
    # Saves to list of created EMLs
    eml_list.append([f'WK{source_country}_{file_name}', confirmation_code])

    '''
    =================================================== Builds Confirmation-TY-LP
    '''

    file_name = (('_').join(campaign_name[1:4]) + '_confirmation-TY-LP')
    with open(file('confirmation-ty-lp'), 'r', encoding='utf-8') as f:
        code = f.read()
    code = regex_product_name.sub(product_name, code)
    code = regex_optional_text.sub(optional_text, code)
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
    confirmation_ty_lp_id = api.eloqua_create_landingpage(file_name, code)[0]

    # Saves to list of created LPs
    lp_list.append([f'WK{source_country}_{file_name}', code])

    '''
    =================================================== Builds Asset E-mail
    '''

    file_name = (('_').join(campaign_name[1:4]) + '_Asset-EML')
    with open(file('asset-eml'), 'r', encoding='utf-8') as f:
        asset_code = f.read()
    asset_code = regex_product_name.sub(product_name, asset_code)
    asset_code = regex_asset_name.sub(asset_name, asset_code)
    asset_code = regex_asset_url.sub(asset_url, asset_code)
    for i in range(len(naming[source_country]['converter']['Placeholders'])):
        placeholder = naming[source_country]['converter']['Placeholders'][i]
        regex_converter = re.compile(rf'{placeholder}', re.UNICODE)
        converter_value = naming[source_country]['converter'][converter_choice][i]
        asset_code = regex_converter.sub(
            rf'{converter_value}', asset_code)
    # Saves to Outcomes file
    print(
        f'{Fore.WHITE}» [{Fore.YELLOW}SAVING{Fore.WHITE}] WK{source_country}_{file_name}')
    with open(file('outcome-file', file_name), 'w', encoding='utf-8') as f:
        f.write(asset_code)
    # Saves to Eloqua
    asset_email_id = api.eloqua_create_email(
        f'WK{source_country}_{file_name}', asset_code)
    # Saves to list of created EMLs
    eml_list.append([f'WK{source_country}_{file_name}', asset_code])

    '''
    =================================================== Update BlindForm
    '''

    # Gets CSS Code of the form
    with open(file('blindform-css'), 'r', encoding='utf-8') as f:
        blindform_css = f.read()

    for field in blindform_json['elements']:
        if field['htmlName'] == 'emailAddress':
            email_field_id = field['id']
        if field['htmlName'] == 'confirmation':
            confirm_field_id = field['id']

    # Gets and prepares processing steps json of the form
    with open(file('blindform-processing'), 'r', encoding='utf-8') as f:
        blindform_processing = json.load(f)
        # Change to string for easy replacing
        blindform_string = json.dumps(blindform_processing)
        blindform_string = blindform_string\
            .replace('EMAIL_FIELD_ID', email_field_id)\
            .replace('SEND_EMAIL_ID', asset_email_id)\
            .replace('TY_LP_ID', confirmation_ty_lp_id)\
            .replace('CONFIRM_FIELD_ID', confirm_field_id)
        # Change back to json for API call
        blindform_processing = json.loads(blindform_string)

    api.eloqua_update_form(
        blindform_id,
        css=blindform_css,
        html=blindform_html,
        processing=blindform_processing['processingSteps']
    )

    '''
    =================================================== Create Campaign
    '''

    # Chosses correct folder ID for campaign
    folder_id = naming[source_country]['id']['campaign'].get(campaign_name[1])

    # Gets campaign code out of the campaign name
    try:
        campaign_code = []
        for part in campaign_name[3].split('-'):
            if part.startswith(tuple(naming[source_country]['psp'])):
                campaign_code.append(part)
        campaign_code = '-'.join(campaign_code)
    except:
        campaign_code = ''

    # Loads json data for campaign canvas creation and fills it with data
    with open(file('content-campaign'), 'r', encoding='utf-8') as f:
        campaign_json = json.load(f)
        # Change to string for easy replacing
        campaign_string = json.dumps(campaign_json)
        campaign_string = campaign_string\
            .replace('ASSET_TYPE', asset_type)\
            .replace('ASSET_EMAIL', asset_email_id)\
            .replace('CONFIRMATION_EMAIL', confirmation_reminder_eml_id)\
            .replace('FORM_ID', form_id)\
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

    print(
        f'\n{SUCCESS}Campaign prepared!',
        f'\n{Fore.WHITE}» Click [Enter] to continue.', end='')
    input(' ')

    return
