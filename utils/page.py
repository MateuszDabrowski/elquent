#!/usr/bin/env python3.6
# -*- coding: utf8 -*-

'''
ELQuent.page
RegEx Eloqua LP & Form automator

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

# Initialize colorama
init(autoreset=True)

# Globals
naming = None
source_country = None

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
        'blank-lp': find_data_file(f'WK{source_country}_LP_blank.txt'),
        'lp-template': find_data_file(f'WK{source_country}_LP_template.txt'),
        'ty-lp': find_data_file(f'WK{source_country}_LP_thank-you.txt'),
        'showhide-css': find_data_file(f'WK{source_country}_LP_showhide-css.txt'),
        'marketing-optin': find_data_file(f'WK{source_country}_FORM_marketing-optin.txt'),
        'email-optin': find_data_file(f'WK{source_country}_FORM_email-optin.txt'),
        'phone-optin': find_data_file(f'WK{source_country}_FORM_phone-optin.txt'),
        'gdpr-info': find_data_file(f'WK{source_country}_FORM_gdpr-info.txt'),
        'submit-button': find_data_file(f'WKCORP_FORM_submit-button.txt'),
        'live-validation': find_data_file(f'WKCORP_FORM_live-validation.txt'),
        'validation-body': find_data_file('WKCORP_FORM_validation-body.txt'),
        'validation-element': find_data_file(f'WK{source_country}_FORM_field-validation.txt'),
        'phone-required': find_data_file(f'WK{source_country}_FORM_required-phone-js.txt'),
        'lead-by-phone': find_data_file(f'WK{source_country}_FORM_lead-by-phone.txt'),
        'showhide-lead': find_data_file(f'WKCORP_LP_showhide-lead.txt'),
        'outcome-file': find_data_file(f'WK{source_country}_{name}.txt', directory='outcomes')
    }

    return file_paths.get(file_path)


'''
=================================================================================
                            GET LANDING PAGE CODE
=================================================================================
'''


def create_landing_page():
    '''
    Returns code of the Landing Page
    '''

    def get_code(choice):
        '''
        Returns Landing Page Code either form clipoard or from template
        '''

        if choice == 2:  # Gets code from clipboard and validates if it is HTML page
            lp_id = api.get_asset_id('landingPage')
            if lp_id:
                lp_code = (api.eloqua_asset_get(
                    lp_id, asset_type='landingPage'))[1]
            else:
                while True:
                    lp_code = pyperclip.paste()
                    is_html = re.compile(r'<html[\s\S\n]*?</html>', re.UNICODE)
                    if is_html.findall(lp_code):
                        print(f'  {SUCCESS}Code copied from clipboard')
                        break
                    print(
                        f'  {ERROR}Invalid HTML. Copy valid code and click [Enter]', end='')
                    input(' ')

            # Modifies landing page code
            lp_code = clean_custom_css(lp_code)
            lp_code = add_showhide_css(lp_code)

        else:  # Gets code from template file
            templates = ['blank-lp', 'lp-template']
            with open(file(templates[choice]), 'r', encoding='utf-8') as f:
                lp_code = f.read()

        return lp_code

    def clean_custom_css(lp_code):
        '''
        Returns LP code without Custom Form CSS
        '''

        custom_css = re.compile(
            r'<!-- StartFormCustomCSS[\s\S]*?EndFormCustomCSS -->', re.UNICODE)
        if custom_css.findall(lp_code):
            print(f'\t{Fore.CYAN}» Cleaning Custom Form CSS')
            lp_code = custom_css.sub('', lp_code)

        return lp_code

    def add_showhide_css(lp_code):
        '''
        Returns LP code with CSS ShowHide solution
        '''

        regex_showhide_exists = re.compile(r'\.read-more-state', re.UNICODE)
        if not regex_showhide_exists.findall(lp_code):
            print(f'\t{Fore.CYAN}» Adding ShowHide CSS')
            with open(file('showhide-css'), 'r', encoding='utf-8') as f:
                css = f.read()
            regex_showhide = re.compile(r'</style>', re.UNICODE)
            lp_code = regex_showhide.sub(css, lp_code, 1)

        return lp_code

    options = [
        f'{Fore.WHITE}[{Fore.YELLOW}TEMPLATE{Fore.WHITE}] Create Blank Page with Form for testing',
        f'{Fore.WHITE}[{Fore.YELLOW}TEMPLATE{Fore.WHITE}] Create Landing Page with Form for campaign',
        f'{Fore.WHITE}[{Fore.YELLOW}EXISTING{Fore.WHITE}] Change form in existing Landing Page'
    ]

    print(f'\n{Fore.GREEN}You can:')
    for i, option in enumerate(options):
        print(f'{Fore.WHITE}[{Fore.YELLOW}{i}{Fore.WHITE}]\t{option}')
    print(
        f'{Fore.WHITE}[{Fore.YELLOW}Q{Fore.WHITE}]\t{Fore.WHITE}[{Fore.YELLOW}Quit to main menu{Fore.WHITE}]')

    while True:
        print(f'{Fore.YELLOW}Enter number associated with your choice:', end='')
        choice = input(' ')
        if choice.lower() == 'q':
            return False
        try:
            choice = int(choice)
        except ValueError:
            print(f'\t{ERROR}Please enter numeric value!')
            continue
        if 0 <= choice < len(options):
            break
        else:
            print(f'{Fore.RED}Entered value does not belong to any utility!')

    return get_code(choice)


'''
=================================================================================
                                GET FORM CODE
=================================================================================
'''


def modify_form(existing_form_id=''):
    '''
    Returns code of new Form
    '''

    def get_form(form_id):
        '''
        Returns validated form code form clipboard
        '''
        # If no ID given via parameters, gets it from user
        if not form_id:
            form_id = api.get_asset_id('form')
        # If there was ID via parameters or given by user
        if form_id:
            form_code = (api.eloqua_asset_get(form_id, asset_type='form'))[1]
        # If input is not valid id
        else:
            while True:
                form_code = pyperclip.paste()
                is_html = re.compile(r'<form[\s\S\n]*?</script>', re.UNICODE)
                if is_html.findall(form_code):
                    print(f'  {SUCCESS}Code copied from clipboard')
                    break
                print(
                    f'  {ERROR}Copied code is not correct Form HTML, please copy again')
                input()

        return form_code

    def lead_phone(form):
        '''
        Returns code of the new Form with phone-based lead mechanism
        '''

        # Searches for phone field in form and if found, returns list of one tuple ("name", "id", "value"). Value might be empty, static or field merge
        regex_phone_field = re.compile(
            r'<input type="text".*?name="(busPhone|telefon)" id="(.+?)".*?value="(.*?)"', re.UNICODE)
        # Tuple deconstructed from single item list
        phone_field = regex_phone_field.findall(form)

        # Asks if phone field should be changed to lead mechanism
        swapping = ''
        if phone_field:
            # Deconstruction from list of single element
            phone_field = phone_field[0]
            while swapping.lower() != 'y' and swapping.lower() != 'n':
                print(
                    f'\t{Fore.WHITE}Change phone field to lead-by-phone mechanism? {Fore.WHITE}({YES}/{NO}):', end=' ')
                swapping = input('')

        if swapping.lower() == 'y':
            # Prepare lead-by-phone snippet with correct values
            with open(file('lead-by-phone'), 'r', encoding='utf-8') as f:
                snippet = f.read()
            # Replace placeholder with correct name
            snippet = snippet.replace('<FIELD_NAME>', phone_field[0])
            # Replace placeholder with correct ID
            snippet = snippet.replace('<FIELD_ID>', phone_field[1])

            # Swap phone field with lead-by-phone mechanism, regex returns list of single tuple ('code', '</div>')
            regex_phone_div = re.compile(
                rf'(<label class="elq-label[| ]" for="{phone_field[1]}">[\s\S]*?(<\/div>[\s]*?){{4}})', re.UNICODE)
            form = regex_phone_div.sub(snippet, form)

            # Find phone validation and append logic for making it required on lead checkbox check: regex returns list of one string
            regex_phone_validation = re.compile(
                rf'(var {phone_field[1]} = new [\s\S]*?\);)', re.UNICODE)
            phone_validation = regex_phone_validation.findall(
                form)[0]  # Deconstruction from list of single element

            # Open phone validation snippet
            with open(file('phone-required'), 'r', encoding='utf-8') as f:
                phone_validation_snippet = f.read()
                # Replace placeholder with correct ID
                phone_validation_snippet = phone_validation_snippet.replace(
                    '<FIELD_ID>', phone_field[1])

            # Append extension to existing field validation
            extended_phone_validation = phone_validation + \
                '\n' + phone_validation_snippet

            # Replace standard validation with extended one
            form = form.replace(
                phone_validation, extended_phone_validation)

            print(f'\t{Fore.CYAN} » Adding lead-by-phone mechanism')

        return form

    def gdpr_info(form):
        '''
        Returns code of the new Form with rodo info about data administrator
        '''

        swapping = ''
        # Asks if information about data administrator should be appended
        while swapping.lower() != 'y' and swapping.lower() != 'n':
            print(
                f'\t{Fore.WHITE}Add information about data administrator? {Fore.WHITE}({YES}/{NO}):', end=' ')
            swapping = input('')

        if swapping.lower() == 'y':
            # Gets place where GDPR info should be appended: regex returns list of one tuple ('code', '</div>')
            regex_submit = re.compile(
                r'((<div class="row"(?:(?!<\/div>)[\s\S])*?"Submit"[\s\S]*?(<\/div>[\s]*?){8}))', re.UNICODE)
            # tuple deconstructed from single array list
            # Deconstruction from list of single element
            submit_div = regex_submit.findall(form)[0]

            # Prepare GDPR information
            with open(file('gdpr-info'), 'r', encoding='utf-8') as f:
                snippet = f.read()

            # Append GDPR information above submit button
            form = form.replace(submit_div[0], submit_div[0] + snippet)

            print(f'\t{Fore.CYAN} » Adding information about data administrator')

        return form

    def swap_optins(form):
        '''
        Returns code of new Form with correct opt ins text
        '''
        optin_paths = {
            'Marketing': file('marketing-optin'),
            'Email': file('email-optin'),
            'Phone': file('phone-optin'),
            'Tracking': file('tracking-optin')  # Currently not used
        }

        # Finds all checkboxes and gets list of tuples ('code', 'name', 'id')
        regex_checkboxes = re.compile(
            r'(<input type="checkbox" name="(.+?)" id="(.+?)">[\s\S]*?<\/label>)', re.UNICODE)
        checkboxes = regex_checkboxes.findall(form)

        # Assigns values to the snippets and swaps them into form code
        optins = naming[source_country]['optins']
        for checkbox in checkboxes:
            if checkbox[1] in optins['Marketing']:
                with open(optin_paths['Marketing'], 'r', encoding='utf-8') as f:
                    optin_text = f.read()
                    # Replace placeholder with correct name
                    optin_text = optin_text.replace(
                        '<FIELD_NAME>', checkbox[1])
                    # Replace placeholder with correct ID
                    optin_text = optin_text.replace(
                        '<FIELD_ID>', checkbox[2])
                    print(
                        f'\t{Fore.CYAN} » Expanding Marketing Opt-in ({checkbox[1]})')
                    form = form.replace(checkbox[0], optin_text)
                continue
            elif checkbox[1] in optins['Email']:
                with open(optin_paths['Email'], 'r', encoding='utf-8') as f:
                    optin_text = f.read()
                    # Replace placeholder with correct name
                    optin_text = optin_text.replace(
                        '<FIELD_NAME>', checkbox[1])
                    # Replace placeholder with correct ID
                    optin_text = optin_text.replace(
                        '<FIELD_ID>', checkbox[2])
                    print(
                        f'\t{Fore.CYAN} » Expanding Email Opt-in ({checkbox[1]})')
                    form = form.replace(checkbox[0], optin_text)
                continue
            elif checkbox[1] in optins['Phone']:
                with open(optin_paths['Phone'], 'r', encoding='utf-8') as f:
                    optin_text = f.read()
                    # Replace placeholder with correct name
                    optin_text = optin_text.replace(
                        '<FIELD_NAME>', checkbox[1])
                    # Replace placeholder with correct ID
                    optin_text = optin_text.replace(
                        '<FIELD_ID>', checkbox[2])
                    print(
                        f'\t{Fore.CYAN} » Expanding Phone Opt-in ({checkbox[1]})')
                    form = form.replace(checkbox[0], optin_text)
                continue
            else:
                form = form.replace(
                    checkbox[0], f'<div class="checkbox-label">{checkbox[0]}</div>')

        return form

    # Gets form and modifies it
    form = get_form(existing_form_id)
    if source_country == 'PL':
        form = gdpr_info(form)
        form = lead_phone(form)
    form = swap_optins(form)

    return form


'''
=================================================================================
                            ADD NEW FORM TO LP CODE
=================================================================================
'''


def swap_form(code, form):
    '''
    Returns LP code with new form
    '''

    regex_style = re.compile(
        r'<style type[\s\S]*?elq-form[\s\S]*?<\/style>', re.UNICODE)
    code = regex_style.sub('', code)
    if '<div class="form">' in code:
        regex_form = re.compile(
            r'(<div class="form">[\s\S]*?<form method[\s\S]*?onsubmit[\s\S]*?function handleFormSubmit[\s\S]*?<\/script>[\s]*?<\/div>)', re.UNICODE)
    else:
        regex_form = re.compile(
            r'(<form method[\s\S]*?onsubmit[\s\S]*?function handleFormSubmit[\s\S]*?<\/script>)', re.UNICODE)
    match = regex_form.findall(code)
    if len(match) == 1:
        code = code.replace(match[0], f'<div class="form">{form}</div>')
        print(f'\t{Fore.GREEN} » Swapping Form in Landing Page')
    elif not match:
        regex_placeholder = re.compile(r'INSERT_FORM')
        is_placeholder = regex_placeholder.findall(code)
        if is_placeholder:
            code = regex_placeholder.sub(form, code)
            print(f'\t{Fore.GREEN} » Adding Form to Landing Page')
        else:
            print(
                f'\t{ERROR}There is no form or placeholder in code.\n',
                f'\t{Fore.WHITE}Add INSERT_FORM to the LP code to mark where you want the Form')
            input(' ')
            raise SystemExit
    elif len(match) >= 1:
        print(f'\t{ERROR}There are {len(match)} forms in the code')
        input(' ')
        raise SystemExit

    # Changes CSS of submit button
    regex_submit_css = re.compile(
        r'.elq-form input\[type=submit\][\s\S\n]*?}', re.UNICODE)
    with open(file('submit-button'), 'r', encoding='utf-8') as f:
        submit_css = f.read()
    code = regex_submit_css.sub(submit_css, code)

    # Fixes margin on checkboxes
    code = code.replace(
        'checkbox-aligned{margin-left:5px;', 'checkbox-aligned{margin-left:0px')

    # Fixes padding on error message, regex returns one element array
    regex_invalid_css = re.compile(r'(.LV_invalid {[\s\S]*?)}')
    invalid_css = regex_invalid_css.findall(code)
    if len(invalid_css) == 2 and 'padding-top' not in invalid_css[1]:
        code = code.replace(
            invalid_css[1], invalid_css[1] + 'padding-top: 10px;')
    elif invalid_css and 'padding-top' not in invalid_css[0]:
        code = code.replace(
            invalid_css[0], invalid_css[0] + 'padding-top: 10px;')

    return code


'''
=================================================================================
                           JavaScript focused functions
=================================================================================
'''


def javascript(code):
    '''
    Returns Landing Page code with proper checkbox js validation
    '''

    def del_validation_js(code):
        '''
        Returns LP code without JavaScript checkbox validation
        '''

        regex_validation = re.compile(
            r'(<script type="text/javascript">[\s\n]*\$\(document\)[\s\S\n]*?requiredChecked[\s\S\n]*?</script>)',
            re.UNICODE)
        if regex_validation.findall(code):
            print(f'\t{Fore.CYAN} » Cleaning Checkbox Validation')
        code = regex_validation.sub('', code)

        return code

    def check_jquery(code):
        '''
        Returns LP code with jQuery import
        '''
        # Looks whether there is already a JQuery and deletes it
        search_jquery = re.compile(r'(jquery)', re.UNICODE)
        if search_jquery.findall(code):
            code = search_jquery.sub('', code)

        # Adds new jquery import to make sure it is appropriate version and placed right
        with open(file('jquery'), 'r', encoding='utf-8') as f:
            jquery = f.read()
        regex_jquery = re.compile(r'(<script)', re.UNICODE)
        code = regex_jquery.sub(jquery, code, 1)
        print(f'\t{Fore.GREEN} » Adding jQuery import')

        return code

    def add_lead_phone_js(code):
        '''
        Returns Landing Page code with lead phone script appended
        '''
        # Looks for old version of the script and deletes it
        regex_old_phone_js = re.compile(
            r'<script>(?:(?!<\/script>)[\s\S])+?#lead_div...toggle[\s\S]+?<\/script>', re.UNICODE)
        if regex_old_phone_js.findall(code):
            code = regex_old_phone_js.sub('', code)

        # Checks if the modern code is already in the page
        if '("#lead_div").show' not in code:
            with open(file('showhide-lead'), 'r', encoding='utf-8') as f:
                lead_script = f.read()
            code = code.replace('</body>', lead_script, 1)

        return code

    def add_live_validation(code):
        '''
        Returns Landing Page code with live validation js added directly isntead of an import
        '''

        # Swaps Eloqua branded LiveValidation import to to direct code snippet
        regex_validation = re.compile(
            r'<script.+?livevalidation_standalone.compressed.js.+?</script>', re.UNICODE)
        validation_import = regex_validation.findall(code)
        if validation_import:
            with open(file('live-validation'), 'r', encoding='utf-8') as f:
                snippet = f.read()
            code = code.replace(validation_import[0], snippet)

        return code

    # Takes care of validation and jquery
    code = del_validation_js(code)
    code = check_jquery(code)
    code = add_live_validation(code)

    # Checks if there is lead-by-phone mechanism
    search_lead_phone = re.compile(r'(name="lead_input")', re.UNICODE)
    is_lead_phone = re.search(search_lead_phone, code)
    if is_lead_phone:
        code = add_lead_phone_js(code)

    return code


'''
=================================================================================
                                SINGLE PAGE FLOW
=================================================================================
'''


def page_gen(country, form_id=''):
    '''
    Main flow for single page creation
    Returns new Landing page code
    '''

    country_naming_setter(country)

    # Checks if there are required source files for the source source_country
    if not os.path.exists(file('validation-element')):
        print(
            f'\t{ERROR}No template found for WK{source_country}.\n{Fore.WHITE}[Enter] to continue.', end='')
        input(' ')
        return False

    # Landing Page code manipulation
    code = create_landing_page()
    if not code:
        return False
    form = modify_form(form_id)
    code = swap_form(code, form)
    code = javascript(code)
    # Swap URLs from non-secure to secure HTTPS by unbranding
    code = code.replace('http://images.go.wolterskluwer.com',
                        'https://img06.en25.com')
    # Delete Custom CSS
    regex_custom_css = re.compile(
        r'<!-- StartFormCustomCSS -->[\s\S]*?<!-- EndFormCustomCSS -->')
    code = regex_custom_css.sub('', code)

    # Two way return of new code
    pyperclip.copy(code)
    with open(file('outcome-file'), 'w', encoding='utf-8') as f:
        f.write(code)
    print(
        f'\n{Fore.GREEN}» You can now paste new Landing Page to Eloqua [CTRL+V].',
        f'\n{Fore.RED}» Remember to update placeholders (PRODUCT_NAME, CONVERTER_5) with correct values!'
        f'\n{Fore.WHITE}  (It is also saved as WK{source_country}_LP.txt in Outcomes folder)',
        f'\n{Fore.WHITE}» Click [Enter] to continue.', end='')
    input(' ')

    return code
