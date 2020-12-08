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
webinar_epoch = None
product_name = None
header_text = None
regex_asset_name = None
regex_asset_url = None
regex_product_name = None
regex_header_text = None
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
        'alert-campaign': find_data_file(f'WK{source_country}_CAMPAIGN_alert.json'),
        'alert-ab-campaign': find_data_file(f'WK{source_country}_CAMPAIGN_alert-ab.json'),
        'ebook-campaign': find_data_file(f'WK{source_country}_CAMPAIGN_ebook.json'),
        'code-campaign': find_data_file(f'WK{source_country}_CAMPAIGN_code.json'),
        'demo-campaign': find_data_file(f'WK{source_country}_CAMPAIGN_demo.json'),
        'webinar-campaign': find_data_file(f'WK{source_country}_CAMPAIGN_webinar.json'),
        'field-merge': find_data_file(f'WK{source_country}_VOUCHER_field-merge.json'),
        'asset-eml': find_data_file(f'WK{source_country}_EML_asset.txt'),
        'demo-eml': find_data_file(f'WK{source_country}_EML_demo.txt'),
        'code-eml': find_data_file(f'WK{source_country}_EML_code.txt'),
        'before-webinar-eml': find_data_file(f'WK{source_country}_EML_before-webinar.txt'),
        'lp-template': find_data_file(f'WK{source_country}_LP_template.txt'),
        'ty-lp': find_data_file(f'WK{source_country}_LP_thank-you.txt'),
        'form-design': find_data_file(f'WK{source_country}_FORM_design-template.json'),
        'form-processing': find_data_file(f'WK{source_country}_FORM_processing-template.json'),
        'form-html': find_data_file(f'WK{source_country}_FORM_html-template.txt'),
        'form-css': find_data_file(f'WK{source_country}_FORM_css-template.txt'),
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


def campaign_first_mail(main_lp_url='', mail_html='', camp_name='', abTest=False, reminder=True):
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

    # if there was not iterated campaign name provided, keep standard campaign name
    if not camp_name:
        camp_name = campaign_name

    # Create e-mail
    if abTest:
        mail_name = ('_'.join(camp_name[0:4]) + '_A-EML')
    else:
        mail_name = ('_'.join(camp_name[0:4]) + '_EML')
    mail_id = api.eloqua_create_email(mail_name, mail_html)

    if not reminder:
        return mail_id

    if abTest:
        reminder_html = mail_html
    else:
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
            reminder_html = regex_mail_preheader.sub(
                reminder_preheader, mail_html)
        else:
            reminder_html = mail_html

    # Create e-mail reminder
    if abTest:
        reminder_name = ('_'.join(camp_name[0:4]) + '_B-EML')
    else:
        reminder_name = ('_'.join(camp_name[0:4]) + '_REM-EML')
    reminder_id = api.eloqua_create_email(reminder_name, reminder_html)

    return (mail_id, reminder_id)


def campaign_main_page(form_id=''):
    '''
    Builds main landing page with main form in Eloqua
    Returns main LP ID and main Form ID
    '''
    # Creates form if there is no id from user
    if not form_id:
        print(
            f'\n{Fore.WHITE}» [{Fore.YELLOW}REQUIRED{Fore.WHITE}] Form for main LP', end='')
    form_html = page.modify_form(form_id)

    # Creates LP
    file_name = ('_'.join(campaign_name[1:4]) + '_LP')
    with open(file('lp-template'), 'r', encoding='utf-8') as f:
        code = f.read()
    code = page.swap_form(code, form_html)
    code = page.javascript(code)
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
    main_form_id = form_id_regex.findall(form_html)[0]

    return (main_lp_id, main_lp_url, main_form_id)


def campaign_main_form():
    '''
    Creates main campaign form in Eloqua
    Returns code, id, and json file of that form
    '''
    form_folder_id = naming[source_country]['id']['form'].get(
        campaign_name[1])

    form_name = '_'.join(campaign_name[0:4]) + '_FORM'
    form_html_name = api.eloqua_asset_html_name(form_name)

    # Loads json data for blindform creation and fills it with name and html_name
    with open(file('form-design'), 'r', encoding='utf-8') as f:
        form_json = json.load(f)
        form_json['name'] = form_name
        form_json['htmlName'] = form_html_name
        form_json['folderId'] = form_folder_id

    # Creates form with given data
    form_id, form_json = api.eloqua_create_form(form_name, form_json)

    # Prepares HTML Code of the form
    with open(file('form-html'), 'r', encoding='utf-8') as f:
        form_html = f.read()
        form_html = form_html.replace('FORM_ID', form_id)

    # Updates form with HTML
    form_id, form_json = api.eloqua_update_form(form_id, html=form_html)

    return (form_html, form_id, form_json)


def campaign_update_form(form_html, form_id, form_json, asset_mail_id, ty_page_id, from_a_form):
    '''
    Updates main form with asset_mail_id, ty_page_id, form_id, from_a_form, psp, lead_status
    '''
    # Gets CSS Code of the form
    with open(file('form-css'), 'r', encoding='utf-8') as f:
        form_css = f.read()

    for field in form_json['elements']:
        if field['htmlName'] == 'emailAddress':
            email_field_id = field['id']
        elif field['htmlName'] == 'firstName':
            firstname_field_id = field['id']
        elif field['htmlName'] == 'lastName':
            lastname_field_id = field['id']
        elif field['htmlName'] == 'jobTitleFreeText1':
            jobtitle_field_id = field['id']
        elif field['htmlName'] == 'company':
            company_field_id = field['id']
        elif field['htmlName'] == 'busPhone':
            phone_field_id = field['id']
        elif field['htmlName'] == 'utm_source':
            source_field_id = field['id']
        elif field['htmlName'] == 'utm_campaign':
            detail_field_id = field['id']
        elif field['htmlName'] == 'utm_medium':
            medium_field_id = field['id']
        elif field['htmlName'] == 'utm_content':
            content_field_id = field['id']
        elif field['htmlName'] == 'utm_term':
            term_field_id = field['id']
        elif field['htmlName'] == 'form_url':
            url_field_id = field['id']
        elif field['htmlName'] == 'directMailOptedIn1':
            dataoptin_field_id = field['id']
        elif field['htmlName'] == 'emailOptedIn1':
            emailoptin_field_id = field['id']
        elif field['htmlName'] == 'phoneOptedIn1':
            phoneoptin_field_id = field['id']

    # Gets PSP Cost from name
    if '/' in campaign_name[4]:
        psp_element = campaign_name[4].split('/')[1]
        cost_code = f'{psp_element}_{campaign_name[5]}'
    else:
        cost_code = campaign_name[3].split('-')
        cost_code = '-'.join(cost_code[-2:])

    # Gets lead-status for product
    while True:
        print(
            f'\n{Fore.YELLOW}»{Fore.WHITE} Write or copypaste {Fore.YELLOW}Lead Status{Fore.WHITE}.')
        lead_status = input(' ')
        if lead_status.startswith(f'WK{source_country}_Lead'):
            break
        else:
            print(f'\n{ERROR}Incorrect Lead Status')

    # Gets and prepares processing steps json of the form
    with open(file('form-processing'), 'r', encoding='utf-8') as f:
        form_processing = json.load(f)
        # Change to string for easy replacing
        form_string = json.dumps(form_processing)
        form_string = form_string\
            .replace('EMAIL_FIELD_ID', email_field_id)\
            .replace('FIRSTNAME_FIELD_ID', firstname_field_id)\
            .replace('LASTNAME_FIELD_ID', lastname_field_id)\
            .replace('COMPANY_FIELD_ID', company_field_id)\
            .replace('JOBTITLE_FIELD_ID', jobtitle_field_id)\
            .replace('PHONE_FIELD_ID', phone_field_id)\
            .replace('SOURCE_FIELD_ID', source_field_id)\
            .replace('DETAIL_FIELD_ID', detail_field_id)\
            .replace('MEDIUM_FIELD_ID', medium_field_id)\
            .replace('CONTENT_FIELD_ID', content_field_id)\
            .replace('TERM_FIELD_ID', term_field_id)\
            .replace('URL_FIELD_ID', url_field_id)\
            .replace('DATAOPTIN_FIELD_ID', dataoptin_field_id)\
            .replace('EMAILOPTIN_FIELD_ID', emailoptin_field_id)\
            .replace('PHONEOPTIN_FIELD_ID', phoneoptin_field_id)\
            .replace('LEAD_STATUS', lead_status)\
            .replace('COST_CODE', cost_code)\
            .replace('CAMPAIGN_ELEMENT_ID', from_a_form)\
            .replace('ASSET_EMAIL_ID', asset_mail_id)\
            .replace('TY_LP_ID', ty_page_id)\
            .replace('FORM_ID', form_id)
        # Change back to json for API call
        form_processing = json.loads(form_string)

    api.eloqua_update_form(
        form_id,
        css=form_css,
        html=form_html,
        processing=form_processing['processingSteps'],
        open_form=True
    )

    return


def campaign_ty_page(asset_name):
    '''
    Builds one or two thank you pages after filling main form
    '''
    file_name = '_'.join(campaign_name[1:4]) + '_TY-LP'

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
    file_name = ('_'.join(campaign_name[1:4]) + '_asset-TECH-EML')
    with open(file('asset-eml'), 'r', encoding='utf-8') as f:
        asset_mail_code = f.read()

    if converter_choice == 'Webinar Access':
        webinar_string = naming[source_country]['webinar']['dateText']
        webinar_string = webinar_string\
            .replace('INSERT_DATE', helper.epoch_to_date(webinar_epoch))\
            .replace('INSERT_HOUR', helper.epoch_to_time(webinar_epoch))
        asset_mail_code = asset_mail_code\
            .replace('<em>"ASSET_NAME"</em>',
                     '<em>"ASSET_NAME"</em>.\n' + webinar_string)

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


def campaign_webinar_mails(asset_name, asset_url):
    '''
    Creates day-before and hour-before e-mails in Eloqua
    Returns mails ids
    '''

    def prepare_mail(before_mail_code):
        '''
        Returns filled e-mail code [string]
        '''
        before_mail_code = regex_product_name.sub(
            product_name, before_mail_code)
        before_mail_code = regex_asset_name.sub(asset_name, before_mail_code)
        before_mail_code = regex_asset_url.sub(asset_url, before_mail_code)
        for i in range(len(naming[source_country]['converter']['Placeholders'])):
            placeholder = naming[source_country]['converter']['Placeholders'][i]
            regex_converter = re.compile(rf'{placeholder}', re.UNICODE)
            converter_value = naming[source_country]['converter'][converter_choice][i]
            before_mail_code = regex_converter.sub(
                rf'{converter_value}', before_mail_code)

        return before_mail_code

    # Gets the before mail template
    with open(file('before-webinar-eml'), 'r', encoding='utf-8') as f:
        before_mail_code = f.read()

    '''
    =================================================== Day Before EML
    '''

    # Creates day before mail
    file_name = ('_'.join(campaign_name[1:4]) + '_day-before-TECH-EML')
    day_before_preheader = naming[source_country]['webinar']['dayBeforePre']
    day_before_content = naming[source_country]['webinar']['dayBeforeContent']
    day_before_mail_code = before_mail_code\
        .replace('PREHEADER_TEXT', day_before_preheader)\
        .replace('CONTENT_TEXT', day_before_content)\
        .replace('INSERT_HOUR', helper.epoch_to_time(webinar_epoch))
    day_before_mail_code = prepare_mail(day_before_mail_code)

    # Saves day before mail to Outcomes file
    print(
        f'{Fore.WHITE}» [{Fore.YELLOW}SAVING{Fore.WHITE}] WK{source_country}_{file_name}')
    with open(file('outcome-file', file_name), 'w', encoding='utf-8') as f:
        f.write(day_before_mail_code)

    # Saves day before mail to Eloqua
    day_before_mail_id = api.eloqua_create_email(
        f'WK{source_country}_{file_name}', day_before_mail_code)

    '''
    =================================================== Hour Before EML
    '''

    # Creates hour before mail
    file_name = ('_'.join(campaign_name[1:4]) + '_hour-before-TECH-EML')
    day_before_preheader = naming[source_country]['webinar']['hourBeforePre']
    day_before_content = naming[source_country]['webinar']['hourBeforeContent']
    hour_before_mail_code = before_mail_code\
        .replace('PREHEADER_TEXT', day_before_preheader)\
        .replace('CONTENT_TEXT', day_before_content)\
        .replace('INSERT_HOUR', helper.epoch_to_time(webinar_epoch))
    hour_before_mail_code = prepare_mail(hour_before_mail_code)

    # Saves hour before mail to Outcomes file
    print(
        f'{Fore.WHITE}» [{Fore.YELLOW}SAVING{Fore.WHITE}] WK{source_country}_{file_name}')
    with open(file('outcome-file', file_name), 'w', encoding='utf-8') as f:
        f.write(hour_before_mail_code)

    # Saves hour before mail to Eloqua
    hour_before_mail_id = api.eloqua_create_email(
        f'WK{source_country}_{file_name}', hour_before_mail_code)

    return (day_before_mail_id, hour_before_mail_id)


def campaign_demo_mail(asset_url):
    '''
    Creates demo e-mail in Eloqua
    Returns demo mail id
    '''
    file_name = ('_'.join(campaign_name[1:4]) + '_demo-TECH-EML')
    with open(file('demo-eml'), 'r', encoding='utf-8') as f:
        demo_mail_code = f.read()

    demo_mail_code = regex_product_name.sub(product_name, demo_mail_code)
    demo_mail_code = regex_asset_url.sub(asset_url, demo_mail_code)

    # Saves to Outcomes file
    print(
        f'{Fore.WHITE}» [{Fore.YELLOW}SAVING{Fore.WHITE}] WK{source_country}_{file_name}')
    with open(file('outcome-file', file_name), 'w', encoding='utf-8') as f:
        f.write(demo_mail_code)

    # Saves to Eloqua
    demo_mail_id = api.eloqua_create_email(
        f'WK{source_country}_{file_name}', demo_mail_code)

    return demo_mail_id


def campaign_code_mail(asset_name, asset_url, code_fieldmerge):
    '''
    Creates code e-mail in Eloqua
    Returns code mail id
    '''
    file_name = ('_'.join(campaign_name[1:4]) + '_code-TECH-EML')
    with open(file('code-eml'), 'r', encoding='utf-8') as f:
        code_mail_code = f.read()

    code_mail_code = regex_product_name.sub(product_name, code_mail_code)
    code_mail_code = regex_asset_name.sub(asset_name, code_mail_code)
    code_mail_code = regex_asset_url.sub(asset_url, code_mail_code)
    code_mail_code = code_mail_code.replace('FIELD_MERGE', code_fieldmerge)

    # Saves to Outcomes file
    print(
        f'{Fore.WHITE}» [{Fore.YELLOW}SAVING{Fore.WHITE}] WK{source_country}_{file_name}')
    with open(file('outcome-file', file_name), 'w', encoding='utf-8') as f:
        f.write(code_mail_code)

    # Saves to Eloqua
    code_mail_id = api.eloqua_create_email(
        f'WK{source_country}_{file_name}', code_mail_code)

    return code_mail_id


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

    # Get short part of campaign_name to differentiate type
    diff_name = '_'.join([campaign_name[2], campaign_name[3].split('-')[0]])

    # Checks if campaign is built with externally generated alert HTML
    alert_mail = True if diff_name.startswith('RET_LA') else False

    # Checks if campaign is built with externally generated newsletter HTML
    newsletter_mail = True if (
        campaign_name[1] == 'MSG' and campaign_name[2] == 'NSL') else False

    # Sets iterations counter based on data from naming.json
    if diff_name in naming[source_country]['mail']['multi_campaigns'].keys():
        iterations = int(naming[source_country]['mail']
                         ['multi_campaigns'][diff_name])
    else:
        iterations = 1

    # Gets main e-mail HTML for simple campaign
    if alert_mail:
        mail_html = mail.alert_constructor(source_country)
    elif newsletter_mail:
        mail_html = mail.newsletter_constructor(source_country)

    # Creates amount of campaigns as per iterations
    for i in range(iterations):

        # Create specific name if multiple iterations
        if iterations > 1:
            custom_name = campaign_name[3].split('-')
            custom_name = custom_name[:1] + [str(i+1)] + custom_name[1:]
            custom_name = '-'.join(custom_name)
            iter_camp_name = campaign_name[:3] + \
                [custom_name] + campaign_name[4:]
        else:
            iter_camp_name = campaign_name

        # Creates main e-mail for simple campaign
        if alert_mail:
            mail_id = campaign_first_mail(
                mail_html=mail_html, camp_name=iter_camp_name, reminder=False)
            if not mail_id:
                return False
        elif newsletter_mail:
            mail_id = campaign_first_mail(
                mail_html=mail_html, camp_name=iter_camp_name, reminder=False)
            if not mail_id:
                return False
        else:
            mail_id = campaign_first_mail(
                camp_name=iter_camp_name, reminder=False)
            if not mail_id:
                return False

        '''
        =================================================== Create Campaign
        '''

        # Gets campaign code out of the campaign name
        campaign_code = []
        if '/' in iter_camp_name[4]:
            psp_element = iter_camp_name[4].split('/')[1]
            campaign_code = f'{psp_element}_{iter_camp_name[5]}'
        else:
            for part in iter_camp_name[3].split('-'):
                if part.startswith(tuple(naming[source_country]['psp'])):
                    campaign_code.append(part)
            campaign_code = '_'.join(campaign_code)

        # Loads json data for campaign canvas creation and fills it with data
        with open(file('simple-campaign'), 'r', encoding='utf-8') as f:
            campaign_json = json.load(f)
            # Change to string for easy replacing
            campaign_string = json.dumps(campaign_json)
            campaign_string = campaign_string.replace('MAIL_ID', mail_id)
            if alert_mail:
                # Capture specific folder
                folder_id = naming[source_country]['id']['campaign'].get(
                    diff_name)
                # Capture specific segment
                segment_id = naming[source_country]['mail']['by_name'][diff_name]['segmentId'][i]
                campaign_string = campaign_string.replace(
                    'SEGMENT_ID', segment_id)
            elif newsletter_mail:
                # Capture specific folder
                folder_id = naming[source_country]['id']['campaign'].get(
                    diff_name)
                # Capture specific segment
                segment_id = naming[source_country]['mail']['by_name'][diff_name]['segmentId'][i]
                campaign_string = campaign_string.replace(
                    'SEGMENT_ID', segment_id)
            else:
                # Capture generic folder for campaign type
                folder_id = naming[source_country]['id']['campaign'].get(
                    iter_camp_name[1])
                # Insert test segment
                campaign_string = campaign_string.replace('SEGMENT_ID', '466')
            # Change back to json for API call
            campaign_json = json.loads(campaign_string)
            campaign_json['name'] = '_'.join(iter_camp_name)
            campaign_json['folderId'] = folder_id
            campaign_json['region'] = iter_camp_name[0]
            campaign_json['campaignType'] = iter_camp_name[2]
            if '/' in iter_camp_name[4]:
                campaign_json['product'] = iter_camp_name[4].split('/')[0]
            else:
                campaign_json['product'] = iter_camp_name[-1]
            campaign_json['fieldValues'][0]['value'] = campaign_code

        # Creates campaign with given data
        api.eloqua_create_campaign(iter_camp_name, campaign_json)

    '''
    =================================================== Finished :)
    '''

    print(f'\n{SUCCESS}Campaign prepared!',
          f'\n{Fore.WHITE}» Click [Enter] to continue.', end='')
    input(' ')

    return


'''
=================================================================================
                                ALERT EMAIL CAMPAIGN FLOW
=================================================================================
'''


def alert_campaign():
    '''
    Main flow for alert email campaign (canvas version)
    Creates filled up alert campaign from package
    Saves html and mjml codes of e-mail as backup to outcome folder
    '''

    # Get short part of campaign_name to differentiate type
    diff_name = '_'.join([campaign_name[2], campaign_name[3].split('-')[0]])

    # Checks if campaign is built with externally generated alert HTML
    alert_mail = True if diff_name.startswith('RET_LA') else False

    # Sets iterations counter based on data from naming.json
    if diff_name in naming[source_country]['mail']['multi_campaigns'].keys():
        iterations = int(naming[source_country]['mail']
                         ['multi_campaigns'][diff_name])
    else:
        iterations = 1

    # Asks whether campaign will implement A/B Testing
    print(f'\n{Fore.YELLOW}» Do you want to A/B Test? '
          f'{Fore.WHITE}({YES}/{NO}):', end='')
    choice = input(' ')
    abTest = True if choice.lower() == 'y' else False

    # Gets main e-mail HTML for simple campaign
    mail_html = mail.alert_constructor(source_country)

    # Creates amount of campaigns as per iterations
    for i in range(iterations):

        # Create specific name if multiple iterations
        if iterations > 1:
            custom_name = campaign_name[3].split('-')
            custom_name = custom_name[:1] + [str(i+1)] + custom_name[1:]
            custom_name = '-'.join(custom_name)
            iter_camp_name = campaign_name[:3] + \
                [custom_name] + campaign_name[4:]
        else:
            iter_camp_name = campaign_name

        # Creates main e-mail for simple campaign
        if abTest:
            mail_id, reminder_id = campaign_first_mail(
                mail_html=mail_html, camp_name=iter_camp_name, abTest=True)
        else:
            mail_id = campaign_first_mail(
                mail_html=mail_html, camp_name=iter_camp_name, reminder=False)
            if not mail_id:
                return False

        '''
        =================================================== Create Campaign
        '''

        # Gets campaign code out of the campaign name
        campaign_code = []
        if '/' in iter_camp_name[4]:
            psp_element = iter_camp_name[4].split('/')[1]
            campaign_code = f'{psp_element}_{iter_camp_name[5]}'
        else:
            for part in iter_camp_name[3].split('-'):
                if part.startswith(tuple(naming[source_country]['psp'])):
                    campaign_code.append(part)
            campaign_code = '_'.join(campaign_code)

        # Loads json data for campaign canvas creation and fills it with data
        template_name = 'alert-ab-campaign' if abTest else 'alert-campaign'

        with open(file(template_name), 'r', encoding='utf-8') as f:
            campaign_json = json.load(f)
            # Change to string for easy replacing
            campaign_string = json.dumps(campaign_json)
            campaign_string = campaign_string.replace('MAIL_ID', mail_id)
            if abTest:
                campaign_string = campaign_string.replace(
                    'REMINDER_ID', reminder_id)
            # Capture specific folder
            folder_id = naming[source_country]['id']['campaign'].get(diff_name)
            # Capture specific segment
            segment_id = naming[source_country]['mail']['by_name'][diff_name]['segmentId'][i]
            campaign_string = campaign_string.replace('SEGMENT_ID', segment_id)
            # Change back to json for API call
            campaign_json = json.loads(campaign_string)
            campaign_json['name'] = '_'.join(iter_camp_name)
            campaign_json['folderId'] = folder_id
            campaign_json['region'] = iter_camp_name[0]
            campaign_json['campaignType'] = iter_camp_name[2]
            if '/' in iter_camp_name[4]:
                campaign_json['product'] = iter_camp_name[4].split('/')[0]
            else:
                campaign_json['product'] = iter_camp_name[-1]
            campaign_json['fieldValues'][0]['value'] = campaign_code

        # Creates campaign with given data
        api.eloqua_create_campaign(iter_camp_name, campaign_json)

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
    if '/' in campaign_name[4]:
        psp_element = campaign_name[4].split('/')[1]
        campaign_code = f'{psp_element}_{campaign_name[5]}'
    else:
        for part in campaign_name[3].split('-'):
            if part.startswith(tuple(naming[source_country]['psp'])):
                campaign_code.append(part)
        campaign_code = '_'.join(campaign_code)

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
        if '/' in campaign_name[4]:
            campaign_json['product'] = campaign_name[4].split('/')[0]
        else:
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

    def ebook_campaign():
        '''
        Returns prepared campaign_json for e-book campaign
        '''
        with open(file('ebook-campaign'), 'r', encoding='utf-8') as f:
            campaign_json = json.load(f)
            # If form is externally hosted, delete LP reporting step from campaign
            if campaign_choice == '4':
                no_lp_elements = []
                for element in campaign_json['elements']:
                    if element['type'] != 'CampaignLandingPage':
                        no_lp_elements.append(element)
                campaign_json['elements'] = no_lp_elements
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
            if '/' in campaign_name[4]:
                campaign_json['product'] = campaign_name[4].split('/')[0]
            else:
                campaign_json['product'] = campaign_name[-1]
            campaign_json['fieldValues'][0]['value'] = campaign_code

        return campaign_json

    def webinar_campaign(day_before_mail_id, hour_before_mail_id):
        '''
        Returns prepared campaign_json for webinar campaign
        '''
        with open(file('webinar-campaign'), 'r', encoding='utf-8') as f:
            campaign_json = json.load(f)
            # If form is externally hosted, delete LP reporting step from campaign
            if campaign_choice == '4':
                no_lp_elements = []
                for element in campaign_json['elements']:
                    if element['type'] != 'CampaignLandingPage':
                        no_lp_elements.append(element)
                campaign_json['elements'] = no_lp_elements
            # Change to string for easy replacing
            campaign_string = json.dumps(campaign_json)
            campaign_string = campaign_string\
                .replace('FIRST_EMAIL', mail_id)\
                .replace('REMINDER_EMAIL', reminder_id)\
                .replace('ASSET_TYPE', asset_type)\
                .replace('ASSET_EMAIL', asset_mail_id)\
                .replace('DAY_BEFORE_EMAIL', day_before_mail_id)\
                .replace('HOUR_BEFORE_EMAIL', hour_before_mail_id)\
                .replace('FORM_ID', main_form_id)\
                .replace('WEBINAR_DATE', str(webinar_epoch))\
                .replace('DAY_BEFORE', str(webinar_epoch - 86400))\
                .replace('DAY_END_BEFORE', str(webinar_epoch - 82800))\
                .replace('HOUR_BEFORE', str(webinar_epoch - 3600))\
                .replace('HOUR_END_BEFORE', str(webinar_epoch - 1800))\
                .replace('LP_ID', main_lp_id)
            # Change back to json for API call
            campaign_json = json.loads(campaign_string)
            campaign_json['name'] = '_'.join(campaign_name)
            campaign_json['folderId'] = folder_id
            campaign_json['region'] = campaign_name[0]
            campaign_json['campaignType'] = campaign_name[2]
            if '/' in campaign_name[4]:
                campaign_json['product'] = campaign_name[4].split('/')[0]
            else:
                campaign_json['product'] = campaign_name[-1]
            campaign_json['fieldValues'][0]['value'] = campaign_code

        return campaign_json

    def code_campaign():
        '''
        Returns prepared campaign_json for code/test campaign
        '''
        # Gets either test template or code template based on user input
        if converter_choice == 'Test Access':
            with open(file('demo-campaign'), 'r', encoding='utf-8') as f:
                campaign_json = json.load(f)
        elif converter_choice == 'Voucher Code':
            with open(file('code-campaign'), 'r', encoding='utf-8') as f:
                campaign_json = json.load(f)
        # If form is externally hosted, delete LP reporting step from campaign
        if campaign_choice == '4':
            no_lp_elements = []
            for element in campaign_json['elements']:
                if element['type'] != 'CampaignLandingPage':
                    no_lp_elements.append(element)
            campaign_json['elements'] = no_lp_elements
        # Change to string for easy replacing
        campaign_string = json.dumps(campaign_json)
        campaign_string = campaign_string\
            .replace('FIRST_EMAIL', mail_id)\
            .replace('REMINDER_EMAIL', reminder_id)\
            .replace('ASSET_TYPE', asset_type)\
            .replace('CODE_EMAIL', asset_mail_id)\
            .replace('FORM_ID', main_form_id)\
            .replace('LP_ID', main_lp_id)
        # Change back to json for API call
        campaign_json = json.loads(campaign_string)
        campaign_json['name'] = '_'.join(campaign_name)
        campaign_json['folderId'] = folder_id
        campaign_json['region'] = campaign_name[0]
        campaign_json['campaignType'] = campaign_name[2]
        if '/' in campaign_name[4]:
            campaign_json['product'] = campaign_name[4].split('/')[0]
        else:
            campaign_json['product'] = campaign_name[-1]
        campaign_json['fieldValues'][0]['value'] = campaign_code

        return campaign_json

    '''
    =================================================== Content campaign globals
    '''

    global converter_choice
    global product_name
    global header_text
    converter_choice, asset_type, asset_name = helper.asset_name_getter()
    if converter_choice in ['Test Access', 'Voucher Code']:
        fieldmerge_name = f'{source_country}_Voucher_{campaign_name[3]}'
        with open(file('field-merge'), 'r', encoding='utf-8') as f:
            fieldmerge_json = json.load(f)
            fieldmerge_json['name'] = fieldmerge_name
            fieldmerge_json['fieldConditions'][0]['condition']['value'] = '_'.join(
                campaign_name)
        code_fieldmerge = api.eloqua_create_fieldmerge(
            fieldmerge_name, fieldmerge_json)
    if converter_choice == 'Test Access':
        asset_url = naming[source_country]['mail']['product_link'] + \
            f'<span%20class=eloquaemail>{code_fieldmerge}</span>'
    else:
        asset_url = helper.asset_link_getter()
    # Gets date if campaign is promoting live webinar
    if converter_choice == 'Webinar Access':
        global webinar_epoch
        webinar_epoch = helper.epoch_getter()
    header_text = helper.header_text_getter()
    product_name = helper.product_name_getter(campaign_name)
    if converter_choice == 'Test Access':
        asset_name = product_name

    '''
    =================================================== Builds campaign assets
    '''

    # Campaign type chooser
    print(
        f'\n{Fore.GREEN}What type of campaign do you want to create?'
        f'\n{Fore.WHITE}[{Fore.YELLOW}1{Fore.WHITE}]\t» [{Fore.YELLOW}Eloqua from scratch{Fore.WHITE}]',
        f'\n{Fore.WHITE}           Creates new Form and new Landing Page'
        f'\n{Fore.WHITE}[{Fore.YELLOW}2{Fore.WHITE}]\t» [{Fore.YELLOW}Eloqua from form{Fore.WHITE}]',
        f'\n{Fore.WHITE}           Creates new Landing Page with existing Form'
        f'\n{Fore.WHITE}[{Fore.YELLOW}3{Fore.WHITE}]\t» [{Fore.YELLOW}Eloqua from landing page{Fore.WHITE}]',
        f'\n{Fore.WHITE}           Creates new Form and updates existing Landing Page'
        f'\n{Fore.WHITE}[{Fore.YELLOW}4{Fore.WHITE}]\t» [{Fore.YELLOW}Externally hosted{Fore.WHITE}]',
        f'\n{Fore.WHITE}           Uses externally hosted Landing Page with Eloqua Form'
    )

    # Creates required assets based on chosen campaign type
    while True:
        print(f'{Fore.YELLOW}Enter number associated with chosen approach:', end='')
        campaign_choice = input(' ')
        if campaign_choice == '1':
            form_html, form_id, form_json = campaign_main_form()
            main_lp_id, main_lp_url, main_form_id = campaign_main_page(form_id)
            break
        elif campaign_choice == '2':
            main_lp_id, main_lp_url, main_form_id = campaign_main_page()
            break
        elif campaign_choice == '3':
            form_html, main_form_id, form_json = campaign_main_form()
            main_lp_id, main_lp_url = page.page_gen(
                source_country, main_form_id)
            break
        elif campaign_choice == '4':
            main_form_id = str(api.get_asset_id('form'))
            main_lp_url, main_lp_id = helper.external_page_getter()
            break
        else:
            print(f'{Fore.RED}Entered value does not belong to any approach!')
            campaign_choice = ''

    # Creates main e-mail and reminder
    mail_id, reminder_id = '', ''
    print(f'\n{Fore.YELLOW}»{Fore.WHITE} Start with e-mail package? {Fore.WHITE}({YES}/{NO}):', end=' ')
    choice = input('')
    if choice.lower() == 'y':
        mail_id, reminder_id = campaign_first_mail(main_lp_url)
        if not mail_id:
            return False

    # Creates thank you page
    ty_page_id = campaign_ty_page(asset_name)

    # Creates asset mail
    if converter_choice not in ['Test Access', 'Voucher Code']:
        asset_mail_id = campaign_asset_mail(asset_name, asset_url)
    elif converter_choice == 'Test Access':
        asset_mail_id = campaign_demo_mail(asset_url)
    elif converter_choice == 'Voucher Code':
        asset_mail_id = campaign_code_mail(
            asset_name, asset_url, code_fieldmerge)

    # Creates day-before and hour-before reminders for Webinar camapaign
    if converter_choice == 'Webinar Access':
        day_before_mail_id, hour_before_mail_id = campaign_webinar_mails(
            asset_name, asset_url)

    '''
    =================================================== Create Campaign
    '''

    # Chosses correct folder ID for campaign
    folder_id = naming[source_country]['id']['campaign'].get(campaign_name[1])

    # Gets campaign code out of the campaign name
    campaign_code = []
    if '/' in campaign_name[4]:
        psp_element = campaign_name[4].split('/')[1]
        campaign_code = f'{psp_element}_{campaign_name[5]}'
    else:
        for part in campaign_name[3].split('-'):
            if part.startswith(tuple(naming[source_country]['psp'])):
                campaign_code.append(part)
        campaign_code = '_'.join(campaign_code)

    # Loads json data for campaign canvas creation and fills it with data
    if converter_choice in ['E-book', 'Webinar Recording']:
        campaign_json = ebook_campaign()
    elif converter_choice == 'Webinar Access':
        campaign_json = webinar_campaign(
            day_before_mail_id, hour_before_mail_id)
    elif converter_choice in ['Test Access', 'Voucher Code']:
        campaign_json = code_campaign()

    # Creates campaign with given data
    _, campaign_json = api.eloqua_create_campaign(campaign_name, campaign_json)

    '''
    =================================================== Finished :)
    '''

    if campaign_choice in ['1', '3']:
        for campaign_step in campaign_json['elements']:
            if '(FaF)' in campaign_step['name']:
                from_a_form = campaign_step['id']

        # Update confirmation blindform
        campaign_update_form(form_html, form_id, form_json,
                             asset_mail_id, ty_page_id, from_a_form)

    print(f'\n{SUCCESS}Campaign prepared!')
    if converter_choice in ['Test Access', 'Voucher Code']:
        print(f'\n{Fore.WHITE}[{Fore.YELLOW}TODO{Fore.WHITE}] Your next steps:',
              f'\n  {Fore.YELLOW}› {Fore.WHITE}Add codes to Code App step',
              f'\n  {Fore.YELLOW}› {Fore.WHITE}Change campaign_name in Voucher Error Notification step',
              f'\n  {Fore.YELLOW}› {Fore.WHITE}Change campaign_name in Submit Code to CDO step')
        if converter_choice == 'Voucher Code':
            print(
                f'  {Fore.YELLOW}› {Fore.WHITE}Update placeholder code-TECH-EML content')
        if converter_choice == 'Test Access':
            print(
                f'  {Fore.YELLOW}› {Fore.WHITE}Update static data in Submit ClickedForm step')
    print(f'{Fore.WHITE}» Click [Enter] to continue.')
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
        f'\n{Fore.WHITE}[{Fore.YELLOW}3{Fore.WHITE}]\t» [{Fore.YELLOW}Alert Canvas{Fore.WHITE}] When you want to send LEX Alert e-mail'
        # f'\n{Fore.WHITE}[{Fore.YELLOW}4{Fore.WHITE}]\t» [{Fore.YELLOW}Content Canvas{Fore.WHITE}] For campaigns with e-books, webinars, codes'
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
            alert_campaign()
            break
        # Currently not available due to massive changes to form code & API
        # elif choice == '4':
        #     campaign_name = helper.campaign_name_getter()
        #     content_campaign()
        #     break
        else:
            print(f'{Fore.RED}Entered value does not belong to any utility!')
            choice = ''

    return
