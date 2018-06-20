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

        if choice == 3:  # Gets code from clipboard and validates if it is HTML page
            lp_id = api.get_asset_id('LP')
            if lp_id:
                lp_code = (api.eloqua_asset_get(lp_id, asset_type='LP'))[1]
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
            templates = ['blank-lp', 'one-column-lp', 'two-column-lp']
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
        f'{Fore.WHITE}[{Fore.YELLOW}TEMPLATE{Fore.WHITE}] Create Blank Landing Page with Form',
        f'{Fore.WHITE}[{Fore.YELLOW}TEMPLATE{Fore.WHITE}] Create One Column Landing Page with Form',
        f'{Fore.WHITE}[{Fore.YELLOW}TEMPLATE{Fore.WHITE}] Create Two Column Landing Page with Form',
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


def create_form():
    '''
    Returns code of new Form
    '''

    def get_form():
        '''
        Returns validated form code form clipoard
        '''
        form_id = api.get_asset_id('Form')
        if form_id:
            form_code = (api.eloqua_asset_get(form_id, asset_type='Form'))[1]
        else:
            while True:
                code = pyperclip.paste()
                is_html = re.compile(r'<form[\s\S\n]*?</script>', re.UNICODE)
                if is_html.findall(code):
                    print(f'  {SUCCESS}Code copied from clipboard')
                    break
                print(f'  {ERROR}Copied code is not correct Form HTML')

        return form_code

    def get_form_fields(form):
        '''
        Returns code of each form field of the new Form
        '''

        form_field = re.compile(
            r'(<div id="formElement[\s\S\n]*?([\s]*?</div>){3})', re.UNICODE)
        form_fields = re.findall(form_field, form)

        return form_fields

    def get_checkboxes(form):
        '''
        Returns list of checkboxes in form of tuples (id, name)
        '''

        # Gets formElement ID, input name and input type
        regex_id_name = re.compile(
            r'formElement(.|..)"[\s\S]*?name="(.+?)"', re.UNICODE)
        id_name = regex_id_name.findall(form)

        # Gets input name and type
        regex_name_type = re.compile(
            r'name="(.*?)".*?type="(.*?)"', re.UNICODE)
        name_type = regex_name_type.findall(form)

        # Builds list of checkboxes with formElement ID and input name
        checkbox = [x for (x, y) in name_type if y == 'checkbox']
        checkbox = [(x, y) for (x, y) in id_name if y in checkbox]

        return checkbox

    def lead_phone(form):
        '''
        Returns code of the new Form with phone-based lead mechanism
        '''

        phone_field = ''
        # Gets the code of phone field
        search_phone_field = re.compile(r'(Numer telefonu)', re.UNICODE)
        for field in get_form_fields(form):
            is_phone_field = re.search(search_phone_field, field[0])  # Boolean
            if is_phone_field:
                phone_field = field[0]
                break
        if not phone_field:
            return form

        # Gets id, name and value (field merge) of phone field
        search_id_name = re.compile(
            r'"formElement(.+?)"[\s\S\n]*?name="(.+?)"', re.UNICODE)
        id_name = re.findall(search_id_name, phone_field)  # List of tuples

        # Asks if phone field should be changed to lead mechanism
        swapping = ''
        while swapping.lower() != 'y' and swapping.lower() != 'n':
            print(
                f'\t{Fore.WHITE}Change phone field to lead-by-phone mechanism? {Fore.WHITE}({YES}/{NO}):', end=' ')
            swapping = input(' ')

        if swapping.lower() == 'y':
            # Prepare lead-by-phone snippet with correct values
            with open(file('lead-by-phone'), 'r', encoding='utf-8') as f:
                snippet = f.read()
            regex_id = re.compile(r'(<FIELD_ID>)', re.UNICODE)
            snippet = regex_id.sub(id_name[0][0], snippet)
            regex_name = re.compile(r'(<FIELD_NAME>)', re.UNICODE)
            snippet = regex_name.sub(id_name[0][1], snippet)

            # Swap phone field with lead-by-phone mechanism
            regex_phone_field = re.compile(
                rf'((<div id="formElement{id_name[0][0]}"[\s\S\n]*?</p>))', re.UNICODE)
            form = regex_phone_field.sub(snippet, form)
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
            swapping = input(' ')

        if swapping.lower() == 'y':
            # Gets place where GDPR info should be appended
            search_checkbox = re.compile(r'type="checkbox"', re.UNICODE)
            search_submit = re.compile(r'type="submit"', re.UNICODE)
            search_id = re.compile(r'"formElement(.*?)"', re.UNICODE)
            for field in get_form_fields(form):
                if search_checkbox.findall(field[0]):
                    form_number = (search_id.findall(field[0]))[0]
                    break
                elif search_submit.findall(field[0]):
                    form_number = (search_id.findall(field[0]))[0]
                    break

            # Prepare GDPR information with correct field id
            with open(file('gdpr-info'), 'r', encoding='utf-8') as f:
                snippet = f.read()
            regex_id = re.compile(r'(<FIELD_ID>)', re.UNICODE)
            snippet = regex_id.sub(form_number, snippet)

            # Add GDPR information to form
            regex_gdpr_info = re.compile(
                rf'(<div id="formElement{form_number}")', re.UNICODE)
            form = regex_gdpr_info.sub(snippet, form)
            print(f'\t{Fore.CYAN} » Adding information about data administrator')

        return form

    def optin_version(form):
        '''
        Returns names of existing marketing, email, phone and tracking optins
        '''
        optins = {}
        # Iterates over possible HTML names of opt-in form fields to save existing optins
        for optin_type in naming[source_country]['optins']:
            for optin_name in naming[source_country]['optins'][optin_type]:
                optin_search = re.compile(rf'name="{optin_name}"', re.UNICODE)
                if optin_search.findall(form):
                    optins[f'{optin_type}'] = f'{optin_name}'

        return optins

    def swap_optins(form, optins):
        '''
        Returns code of new Form with correct opt ins text
        '''
        optin_paths = {
            'Marketing': file('marketing-optin'),
            'Email': file('email-optin'),
            'Phone': file('phone-optin'),
            'Tracking': file('tracking-optin')
        }

        # Creates dict of {(optin_type, optin_path): 'in_form_optin_name'}
        form_optins = {}
        for optin in naming[source_country]['optins']:
            for name in optins.values():
                if name in naming[source_country]['optins'][optin]:
                    form_optins[optin] = name

        if len(form_optins) != len(optins):
            error = f'\t{ERROR}Non standard HTML name of opt-in form field\n'
            raise ValueError(error)

        for optin in form_optins.items():
            # Loads opt-in new code
            file_path = optin_paths[optin[0]]
            with open(file_path, 'r', encoding='utf-8') as f:
                optin_text = f.read()
            # Create regex to swap opt-in in form code
            regex_optin = re.compile(
                rf'<input name="{optin[1]}"[\s\S]*?<\/p>', re.UNICODE)

            # Swaps HTML name of opt-in to language correct
            regex_language = re.compile(r'<INSERT_OPTIN>', re.UNICODE)
            optin_text = regex_language.sub(rf'{optin[1]}', optin_text)

            # Adds new opt-ins to form code
            print(f'\t{Fore.CYAN} » Expanding {optin[0]} Opt-in ({optin[1]})')
            form = regex_optin.sub(optin_text, form)

        form, requiredOptins = required_checkboxes(
            form, optins)

        return (form, requiredOptins)

    def required_checkboxes(form, optins):
        '''
        Returns full list of required checkboxes
        '''

        checkbox = get_checkboxes(form)
        required_checkbox = []
        unknown_checkbox = [(x, y)
                            for (x, y) in checkbox if y not in optins.values()]

        # Ask user which additional checkboxes are required
        for checkbox in unknown_checkbox:
            required = ''
            while required.lower() != 'y' and required.lower() != 'n' and required.lower() != '0':
                print(
                    f'\t{Fore.WHITE}Is "{checkbox[1]}" checkbox required? {Fore.WHITE}({YES}/{NO}):', end=' ')
                required = input(' ')
            if required.lower() == 'y':
                required_checkbox += (checkbox,)
                regex_req = re.compile(
                    rf'(formElement{checkbox[0]}[\s\S]*?checkbox-label")( >)', re.UNICODE)
                form = regex_req.sub(
                    r'\1 ><span class="required">*</span> ', form, 1)
                print(f'\t{Fore.CYAN} » Adding {checkbox[1]} as required')
            elif required.lower() == 'n':
                print(f'\t{Fore.CYAN} » Setting {checkbox[1]} as not required')
            elif required == '0':
                print(
                    f'\t{Fore.CYAN} » Setting all left checkboxes as not required')
                break

        return (form, required_checkbox)

    # Gets form and modifies it
    form = get_form()
    if source_country == 'PL':
        form = gdpr_info(form)
        form = lead_phone(form)
    optins = optin_version(form)
    form, required = swap_optins(form, optins)

    return (form, required)


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
    regex_form = re.compile(
        r'<div>\s*?<form method[\s\S]*?dom0[\s\S]*?<\/script>\s*?<\/div>', re.UNICODE)
    match = regex_form.findall(code)
    if len(match) == 1:
        code = regex_form.sub(form, code)
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

    # Appends Unicode arrow to button text
    regex_submit_text = re.compile(
        r'(?<=<input type="submit" value=)"(.*?)"', re.UNICODE)
    if regex_submit_text.findall(code):
        button_text = '"' + (4 * '&nbsp;&zwnj; ') + \
            regex_submit_text.findall(code)[0] + ' →"'
        code = regex_submit_text.sub(button_text, code)

    return code


'''
=================================================================================
                           JavaScript focused functions
=================================================================================
'''


def javascript(code, required, ):
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

        search_jquery = re.compile(r'(jquery)', re.UNICODE)
        is_jquery = re.search(search_jquery, code)
        if not is_jquery:
            with open(file('jquery'), 'r', encoding='utf-8') as f:
                jquery = f.read()
            regex_jquery = re.compile(r'(<script)', re.UNICODE)
            code = regex_jquery.sub(jquery, code, 1)
            print(f'\t{Fore.GREEN} » Adding jQuery import')

        return code

    def add_validation_js(code, required):
        '''
        Returns LP code with new JavaScript checkbox validation
        '''

        # Adds checkbox validation body to LP code
        with open(file('validation-body'), 'r', encoding='utf-8') as f:
            validation_body = f.read()
        regex_validation = re.compile(r'</body>', re.UNICODE)
        code = regex_validation.sub(validation_body, code)

        # Adds checkbox validation element to LP code
        regex_element_id = re.compile(r'INSERT_ID', re.UNICODE)
        regex_element_name = re.compile(r'INSERT_NAME', re.UNICODE)
        regex_element_insert = re.compile(r'//requiredChecked', re.UNICODE)
        for req in required:
            with open(file('validation-element'), 'r', encoding='utf-8') as f:
                validation_element = f.read()
            validation_element = regex_element_id.sub(
                req[0], validation_element)
            validation_element = regex_element_name.sub(
                req[1], validation_element)
            code = regex_element_insert.sub(validation_element, code)
        print(f'\t{Fore.GREEN} » Adding new Checkbox Validation')

        return code

    def add_lead_phone_js(code):
        '''
        Returns Landing Page code with lead phone script appended
        '''

        # Checks if there already is that code
        search_lead_script = re.compile(r'(#lead_input)', re.UNICODE)
        is_lead_script = re.search(search_lead_script, code)
        if not is_lead_script:
            with open(file('showhide-lead'), 'r', encoding='utf-8') as f:
                lead_script = f.read()
            regex_lead_script = re.compile(r'(</body>)', re.UNICODE)
            code = regex_lead_script.sub(lead_script, code)

        return code

    # Takes care of checkbox validation scripts
    code = del_validation_js(code)
    code = check_jquery(code)
    if required:  # Add script only if there is at least one required
        code = add_validation_js(code, required)

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


def page_gen(country):
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
    form, required = create_form()
    code = swap_form(code, form)
    code = javascript(code, required)

    # Two way return of new code
    pyperclip.copy(code)
    with open(file('outcome-file'), 'w', encoding='utf-8') as f:
        f.write(code)
    print(
        f'\n{Fore.GREEN}» You can now paste new Landing Page to Eloqua [CTRL+V].',
        f'\n{Fore.WHITE}  (It is also saved as WK{source_country}_LP.txt in Outcomes folder)',
        f'\n{Fore.WHITE}» Click [Enter] to continue.', end='')
    input(' ')

    return code
