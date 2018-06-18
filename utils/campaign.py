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
from colorama import Fore, init

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
SUCCESS = f'{Fore.WHITE}[{Fore.GREEN}SUCCESS{Fore.WHITE}] '


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
        'jquery': find_data_file('WKCORP_jquery.txt'),
        'blindform': find_data_file(f'WK{source_country}_blindform.json'),
        'blindform-html': find_data_file(f'WK{source_country}_blindform-html.txt'),
        'blindform-css': find_data_file(f'WK{source_country}_blindform-css.txt'),
        'blindform-processing': find_data_file(f'WK{source_country}_blindform-processing.json'),
        'simple-campaign': find_data_file(f'WK{source_country}_simple-campaign.json'),
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


def campaign_first_mail():
    '''
    Creates first mail and its reminder
    Returns eloqua id of both
    '''
    # Creates first mail from package
    mail_html = mail.mail_constructor(source_country, campaign=True)

    regex_mail_preheader = re.compile(
        r'<!--pre-start.*?pre-end-->', re.UNICODE)
    print(f'\n{Fore.YELLOW}»{Fore.WHITE} Write or paste {Fore.YELLOW}pre-header{Fore.WHITE} text for',
          f'{Fore.YELLOW}reminder{Fore.WHITE} e-mail and click [Enter]',
          f'\n{Fore.WHITE}[S]kip to keep the same pre-header as in main e-mail.')
    reminder_preheader = input(' ')
    if reminder_preheader.lower() != 's':
        reminder_preheader = '<!--pre-start-->' + reminder_preheader + '<!--pre-end-->'
        reminder_html = regex_mail_preheader.sub(reminder_preheader, mail_html)
    else:
        reminder_html = html

    # Create e-mail
    mail_name = (('_').join(campaign_name[0:4]) + '_EML')
    print(mail_name)
    mail_id = api.eloqua_create_email(mail_name, mail_html)

    # Create e-mail reminder
    reminder_name = (('_').join(campaign_name[0:4]) + '_reminder-EML')
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
    with open(file('two-column-lp'), 'r', encoding='utf-8') as f:
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
    main_lp_id = api.eloqua_create_landingpage(file_name, code)[0]

    # Gets main form id for future campaign canvas API calls
    form_id_regex = re.compile(r'id="form(\d+?)"', re.UNICODE)
    main_form_id = form_id_regex.findall(form)[0]

    return (main_lp_id, main_form_id)


def campaign_ty_page(lead_or_contact_form):
    '''
    Builds one or two thank you pages after filling main form
    '''
    def create_ty_page(lp_type=''):
        '''
        Modifies code of selected type of thank you page
        '''
        if lp_type == 'lead':
            file_name = (('_').join(campaign_name[1:4]) + '_lead-TY-LP')
            with open(file('conversion-lead'), 'r', encoding='utf-8') as f:
                conversion_script = f.read()
        if lp_type == 'contact':
            file_name = (('_').join(campaign_name[1:4]) + '_contact-TY-LP')
            with open(file('conversion-contact'), 'r', encoding='utf-8') as f:
                conversion_script = f.read()

        # Modify TY LP code
        regex_conversion_script = re.compile(r'(</body>)', re.UNICODE)
        ty_lp = regex_conversion_script.sub(conversion_script, code)
        ty_lp = regex_gtm.sub(f'WK{source_country}_{file_name}', ty_lp)
        for i in range(len(naming[source_country]['converter']['Placeholders'])):
            placeholder = naming[source_country]['converter']['Placeholders'][i]
            regex_converter = re.compile(rf'{placeholder}', re.UNICODE)
            converter_value = naming[source_country]['converter'][converter_choice][i]
            lead_ty_lp = regex_converter.sub(rf'{converter_value}', ty_lp)

        # Adds information about presentation for lead TY Page
        if lp_type == 'lead':
            lead_ty_lp = lead_ty_lp.replace(
                '<!-- PRESENTATION -->', naming[source_country]['converter']['Presentation'])

        # Saves to Outcomes file
        print(
            f'{Fore.WHITE}» [{Fore.YELLOW}SAVING{Fore.WHITE}] WK{source_country}_{file_name}')
        with open(file('outcome-file', file_name), 'w', encoding='utf-8') as f:
            f.write(ty_lp)

        # Saves to Eloqua
        api.eloqua_create_landingpage(file_name, ty_lp)

        return

    # Gets and prepares general TY LP structure
    with open(file('ty-lp'), 'r', encoding='utf-8') as f:
        code = f.read()
    code = regex_product_name.sub(product_name, code)
    code = regex_header_text.sub(header_text, code)

    if lead_or_contact_form == 0 or lead_or_contact_form == 1:
        create_ty_page(lp_type='lead')
    if lead_or_contact_form == 0 or lead_or_contact_form == 2:
        create_ty_page(lp_type='contact')

    return


def campaign_create_blindform():
    '''
    Creates blindform in Eloqua
    Returns code, id, html name and json file of that blindform
    '''
    blindform_folder_id = naming[source_country]['id']['form'].get(
        campaign_name[1])

    blindform_name = (('_').join(
        campaign_name[0:4]) + '_confirmation-blindFORM')
    blindform_html_name = api.eloqua_asset_html_name(blindform_name)

    # Loads json data for blindform creation and fills it with name and html_name
    with open(file('blindform'), 'r', encoding='utf-8') as f:
        blindform_json = json.load(f)
        blindform_json['name'] = blindform_name
        blindform_json['htmlName'] = blindform_html_name
        blindform_json['folderId'] = blindform_folder_id

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

    return (blindform_html, blindform_id, blindform_json, blindform_html_name)


def campaign_confirmation_page(blindform_html):
    '''
    Builds confirmation landing page in Eloqua
    '''
    file_name = (('_').join(campaign_name[1:4]) + '_confirmation-LP')
    with open(file('confirmation-lp'), 'r', encoding='utf-8') as f:
        code = f.read()
    code = page.swap_form(code, blindform_html)
    code = page.javascript(code, required=None)
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
    api.eloqua_create_landingpage(file_name, code)

    return


def campaign_confirmation_mail(blindform_html_name, asset_name):
    '''
    Creates set of conifrmation mails in Eloqua
    Returns confirmation reminder email id
    '''
    # Builds code of e-mail
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

    # Saves standard + reminder
    for mail_name in ['_confirmation-EML', '_confirmation-reminder-EML']:
        file_name = (('_').join(campaign_name[1:4]) + mail_name)

        # Saves to Outcomes file
        print(
            f'{Fore.WHITE}» [{Fore.YELLOW}SAVING{Fore.WHITE}] WK{source_country}_{file_name}')
        with open(file('outcome-file', file_name), 'w', encoding='utf-8') as f:
            f.write(confirmation_code)

        # Saves to Eloqua -> first id is overwritten by reminder ID and only second is returned
        confirmation_reminder_mail_id = api.eloqua_create_email(
            f'WK{source_country}_{file_name}', confirmation_code)

    return confirmation_reminder_mail_id


def confirmation_ty_page():
    '''
    Builds in Eloqua confirmation thank you page
    Returns it's eloqua id
    '''
    file_name = (('_').join(campaign_name[1:4]) + '_confirmation-TY-LP')
    with open(file('confirmation-ty-lp'), 'r', encoding='utf-8') as f:
        code = f.read()
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
    confirmation_ty_lp_id = api.eloqua_create_landingpage(file_name, code)[0]

    return confirmation_ty_lp_id


def campaign_asset_mail(asset_name, asset_url):
    '''
    Creates asset e-mail in Eloqua
    Returns asset mail id
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
        asset_code = regex_converter.sub(rf'{converter_value}', asset_code)

    # Saves to Outcomes file
    print(
        f'{Fore.WHITE}» [{Fore.YELLOW}SAVING{Fore.WHITE}] WK{source_country}_{file_name}')
    with open(file('outcome-file', file_name), 'w', encoding='utf-8') as f:
        f.write(asset_code)

    # Saves to Eloqua
    asset_mail_id = api.eloqua_create_email(
        f'WK{source_country}_{file_name}', asset_code)

    return asset_mail_id


def campaign_update_blindform(blindform_html, blindform_id, blindform_json, asset_mail_id, confirmation_ty_lp_id):
    '''
    Updates confirmation blindform with asset id's
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
            .replace('SEND_EMAIL_ID', asset_mail_id)\
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

    return


'''
=================================================================================
                                SIMPLE CAMPAIGN FLOW
=================================================================================
'''


def simple_campaign():
    '''
    Main flow for simple campaign (mail + reminder)
    Creates filled up campaign in Eloqua along with assets from package
    Saves html and mjml codes of e-mail as backup to outcome folder
    '''

    # Creates main e-mail and reminder
    mail_id, reminder_id = campaign_first_mail()

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
    with open(file('simple-campaign'), 'r', encoding='utf-8') as f:
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
                                ASSET CAMPAIGN FLOW
=================================================================================
'''


def content_campaign():
    '''
    Main flow for content campaign
    Creates filled up campaign in Eloqua along with assets
    Saves multiple html codes as backup to outcome folder
    '''

    global converter_choice
    global product_name
    global header_text
    lead_or_contact_form = helper.campaign_type_getter()
    converter_choice, asset_type, asset_name = helper.asset_name_getter()
    asset_url = helper.asset_link_getter()
    product_name = helper.product_name_getter(campaign_name)
    header_text = helper.header_text_getter()

    '''
    =================================================== Campaign specific regex compiles
    '''
    global regex_blindform_html_name
    regex_blindform_html_name = re.compile('HTML_FORM_NAME', re.UNICODE)

    '''
    =================================================== Builds campaign assets
    '''
    # Create main page with selected form
    main_lp_id, main_form_id = campaign_main_page()

    # Create one or two thank you pages depending on previous user input
    campaign_ty_page(lead_or_contact_form)

    # Create confirmation blindform for confirmation e-mail and landing page
    blindform_html, blindform_id, blindform_json, blindform_html_name = campaign_create_blindform()

    # Create confirmation landing page
    campaign_confirmation_page(blindform_html)

    # Create set of confirmation mails
    confirmation_reminder_mail_id = campaign_confirmation_mail(
        blindform_html_name, asset_name)

    # Create confirmation thank you page
    confirmation_ty_lp_id = confirmation_ty_page()

    # Create asset mail
    asset_mail_id = campaign_asset_mail(asset_name, asset_url)

    # Update confirmation blindform
    campaign_update_blindform(
        blindform_html, blindform_id, blindform_json, asset_mail_id, confirmation_ty_lp_id)

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
    with open(file('content-campaign'), 'r', encoding='utf-8') as f:
        campaign_json = json.load(f)
        # Change to string for easy replacing
        campaign_string = json.dumps(campaign_json)
        campaign_string = campaign_string\
            .replace('ASSET_TYPE', asset_type)\
            .replace('ASSET_EMAIL', asset_mail_id)\
            .replace('CONFIRMATION_EMAIL', confirmation_reminder_mail_id)\
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
        f'\n{Fore.GREEN}ELQuent.campaign Utilites:'
        f'\n{Fore.WHITE}[{Fore.YELLOW}1{Fore.WHITE}]\t» [{Fore.YELLOW}Simple{Fore.WHITE}] Campaign with just e-mail and reminder'
        f'\n{Fore.WHITE}[{Fore.YELLOW}2{Fore.WHITE}]\t» [{Fore.YELLOW}Content{Fore.WHITE}] Campaign with e-book/webinar/code/etc'
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
            content_campaign()
            break
        else:
            print(f'{Fore.RED}Entered value does not belong to any utility!')
            choice = ''

    return
