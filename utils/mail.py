#!/usr/bin/env python3.6
# -*- coding: utf8 -*-

'''
ELQuent.mail
E-mail package constructor (RegEx + API)

Mateusz Dąbrowski
github.com/MateuszDabrowski
linkedin.com/in/mateusz-dabrowski-marketing/
'''

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


def file(file_path, file_name='', folder_name=''):
    '''
    Returns file path to template files
    '''

    def find_data_file(filename, directory='incomes', folder_name=''):
        '''
        Returns correct file path for both script and frozen app
        '''
        if directory == 'main':  # Files in main directory
            if getattr(sys, 'frozen', False):
                datadir = os.path.dirname(sys.executable)
            else:
                datadir = os.path.dirname(os.path.dirname(__file__))
            return os.path.join(datadir, filename)
        elif directory == 'api':  # For reading api files
            if getattr(sys, 'frozen', False):
                datadir = os.path.dirname(sys.executable)
            else:
                datadir = os.path.dirname(os.path.dirname(__file__))
            return os.path.join(datadir, 'utils', directory, filename)
        elif directory == 'incomes':  # For reading user files
            if getattr(sys, 'frozen', False):
                datadir = os.path.dirname(sys.executable)
            else:
                datadir = os.path.dirname(os.path.dirname(__file__))
            return os.path.join(datadir, directory, filename)
        elif directory == 'outcomes':  # For writing outcome files
            if getattr(sys, 'frozen', False):
                datadir = os.path.dirname(sys.executable)
            else:
                datadir = os.path.dirname(os.path.dirname(__file__))
            return os.path.join(datadir, directory, filename)
        elif directory == 'package':  # For reading package files
            if getattr(sys, 'frozen', False):
                datadir = os.path.dirname(sys.executable)
            else:
                datadir = os.path.dirname(os.path.dirname(__file__))
            return os.path.join(datadir, 'incomes', folder_name, filename)

    file_paths = {
        'naming': find_data_file('naming.json', directory='api'),
        'incomes': find_data_file('incomes', directory='main'),
        'package': find_data_file(f'{file_name}'),
        'package_file': find_data_file(f'{file_name}', directory='package', folder_name=folder_name),
        'mail_html': find_data_file(f'WK{source_country}_{file_name}.txt', directory='outcomes'),
        'mail_mjml': find_data_file(f'WK{source_country}_{file_name}.mjml', directory='outcomes')
    }

    return file_paths.get(file_path)


'''
=================================================================================
                            Preparation of the program
=================================================================================
'''


def package_chooser():
    '''
    Informs if there is any problem with income folder.
    Returns package name and files in chosen package.
    '''
    # Gets list of packages in Income folder
    folders = os.listdir(file('incomes'))
    folders = [folder for folder in folders if not folder.startswith('.')]

    # Prints available packages with info about their content
    packages = {}
    print(f'\n{Fore.GREEN}Available packages:', end='')
    for i, folder in enumerate(folders):
        try:
            files = os.listdir(file('package', file_name=folder))
        except NotADirectoryError:
            print(
                f'\n{Fore.YELLOW}There is non-folder file in Incomes.',
                f'\n{Fore.WHITE}Please put it inside a folder to see it listed here.')
            continue
        files = [f for f in files if not f.startswith('.')]
        html = [f for f in files if f.endswith('.html')]
        mjml = [f for f in files if f.endswith('.mjml')]
        img = [f for f in files if f.endswith(
            '.jpg') or f.endswith('.png') or f.endswith('.gif')]
        packages[folder] = {'html': html, 'mjml': mjml, 'img': img}
        print(f'\n{Fore.WHITE}[{Fore.YELLOW}{i}{Fore.WHITE}] {folder}',
              f'\n{Fore.WHITE}    Files: [{Fore.YELLOW}MJML: {len(mjml)}{Fore.WHITE}]',
              f'{Fore.WHITE}[{Fore.YELLOW}HTML: {len(html)}{Fore.WHITE}]',
              f'{Fore.WHITE}[{Fore.YELLOW}IMG: {len(img)}{Fore.WHITE}]')
    print(f'\n{Fore.WHITE}[{Fore.YELLOW}Q{Fore.WHITE}] Quit to main menu')
    print(f'{Fore.YELLOW}Enter number associated with chosen package:', end='')
    choice = input(' ')

    # Allows user to pick which package should be build
    while True:
        if not choice:
            print(
                f'{Fore.YELLOW}Enter number associated with chosen package:', end='')
            choice = input(' ')
        if choice.lower() == 'q':
            return False, False, False, False
        try:
            choice = int(choice)
        except (TypeError, ValueError):
            print(f'{ERROR}Please enter numeric value!')
            choice = ''
            continue
        if 0 <= choice < len(folders):
            break
        else:
            print(f'{ERROR}Entered value does not belong to any package!')
            choice = ''

    folder_name = folders[choice]
    return (
        folder_name,
        packages.get(folder_name).get('html'),
        packages.get(folder_name).get('mjml'),
        packages.get(folder_name).get('img')
    )


'''
=================================================================================
                                Code Manipulation Helpers
=================================================================================
'''


def link_manipulator(code_file, trackable_links, utm):
    '''
    Appends PURL, UTM & elqTrack to viable links and changes CDN to SSL Eloqua one
    '''
    utm_element = re.compile(r'(&|)(utm.*?)(?=(&|"))', re.UNICODE)
    for link in trackable_links:
        if 'info.wolterskluwer' in link and link[-2] == '/':
            code_file = code_file.replace(
                link, (link[:-1] + '<span class=eloquaemail >PURL_NAME1</span>' + utm + '"'))
        elif 'info.wolterskluwer' in link and link[-2] != '/':
            code_file = code_file.replace(
                link, (link[:-1] + '/<span class=eloquaemail >PURL_NAME1</span>' + utm + '"'))
        elif utm.lower() != 's':
            new_link = link
            # Cleans old tracking script if any
            if 'utm_' in link:
                new_link = utm_element.sub('', link)
                new_link = new_link.replace('?"', '"')
            # Appends new tracking script
            if '?' in new_link:
                code_file = code_file.replace(
                    link, (new_link[:-1] + '&' + utm[1:] + '&elqTrack=true"'))
            else:
                code_file = code_file.replace(
                    link, (new_link[:-1] + utm + '&elqTrack=true"'))
        elif utm.lower() == 's':
            if '?' in link:
                code_file = code_file.replace(
                    link, (link[:-1] + '&elqTrack=true"'))
            else:
                code_file = code_file.replace(
                    link, (link[:-1] + '?elqTrack=true"'))

    # Swaps file storage links to unbranded SSL
    code_file = code_file.replace(
        'http://images.go.wolterskluwer.com', 'https://img06.en25.com')

    return code_file


'''
=================================================================================
                                Code Output Helper
=================================================================================
'''


def output_method(html_code='', mjml_code=''):
    '''
    Allows user choose how the program should output the results
    Returns email_id if creation/update in Eloqua was selected
    '''
    # Asks which output
    print(
        f'\n{Fore.GREEN}New code should be:',
        f'\n{Fore.WHITE}[{Fore.YELLOW}0{Fore.WHITE}]\t»',
        f'{Fore.WHITE}[{Fore.YELLOW}FILE{Fore.WHITE}] Only saved to Outcomes folder')
    if html_code:
        print(
            f'{Fore.WHITE}[{Fore.YELLOW}1{Fore.WHITE}]\t»',
            f'{Fore.WHITE}[{Fore.YELLOW}HTML{Fore.WHITE}] Copied to clipboard as HTML for pasting [CTRL+V]')
    if mjml_code:
        print(
            f'{Fore.WHITE}[{Fore.YELLOW}2{Fore.WHITE}]\t»',
            f'{Fore.WHITE}[{Fore.YELLOW}MJML{Fore.WHITE}] Copied to clipboard as MJML for pasting [CTRL+V]')
    print(
        f'{Fore.WHITE}[{Fore.YELLOW}3{Fore.WHITE}]\t»',
        f'{Fore.WHITE}[{Fore.YELLOW}CREATE{Fore.WHITE}] Uploaded to Eloqua as a new E-mail',
        f'\n{Fore.WHITE}[{Fore.YELLOW}4{Fore.WHITE}]\t»',
        f'{Fore.WHITE}[{Fore.YELLOW}UPDATE{Fore.WHITE}] Uploaded to Eloqua as update to existing E-mail')
    email_id = ''
    while True:
        print(f'{Fore.YELLOW}Enter number associated with chosen utility:', end='')
        choice = input(' ')
        if choice == '0':
            break
        elif choice == '1' and html_code:
            pyperclip.copy(html_code)
            print(
                f'\n{SUCCESS}You can now paste the HTML code [CTRL+V]')
            break
        elif choice == '2' and mjml_code:
            pyperclip.copy(mjml_code)
            print(
                f'\n{SUCCESS}You can now paste the MJML code [CTRL+V]')
            break
        elif choice == '3':
            print(
                f'\n{Fore.WHITE}[{Fore.YELLOW}NAME{Fore.WHITE}] » Write or copypaste name of the E-mail:')
            name = api.eloqua_asset_name()
            api.eloqua_create_email(name, html_code)
            break
        elif choice == '4':
            print(
                f'\n{Fore.WHITE}[{Fore.YELLOW}ID{Fore.WHITE}] » Write or copypaste ID of the E-mail to update:')
            email_id = input(' ')
            if not email_id:
                email_id = pyperclip.paste()
            api.eloqua_update_email(email_id, html_code)
            break
        else:
            print(f'{ERROR}Entered value does not belong to any utility!')
            choice = ''

        return


'''
=================================================================================
                                Alert Mail Helper
=================================================================================
'''


def generator_constructor(country, generated_mail):
    '''
    Gets, fixes and uploads alert mail code to Eloqua
    Returns eloqua mail id
    '''

    # Create global source_country and load json file with naming convention
    country_naming_setter(country)

    '''
    =================================================== Get HTML
    '''

    # Asks user to firstly upload images to Eloqua
    print(
        f'\n{Fore.YELLOW}» {Fore.WHITE}Please add email folder with HTML file to Incomes folder.',
        f'\n{Fore.WHITE}[Enter] to continue when finished.', end='')
    input(' ')

    # Lets user choose package to construct
    while True:
        # Gets name and files but image_files with index 3
        folder_name, html_files, _, _ = package_chooser()
        if not folder_name:
            return False
        if not html_files:
            print(
                f'{ERROR}Chosen package doesn\'t have HTML file!')
        else:
            break

    mail_html = ''
    if html_files:
        with open(file('package_file', file_name=html_files[0], folder_name=folder_name), 'r', encoding='utf-8') as f:
            mail_html = f.read()

    '''
    =================================================== Modify package
    '''

    # Gathers all links in HTML
    links = re.compile(r'href=(".*?")', re.UNICODE)
    trackable_links = links.findall(mail_html)
    trackable_links = list(set(trackable_links))

    # Removes untrackable links
    for link in trackable_links[:]:
        if not link or 'googleapis' in link or 'emailfield' in link:
            trackable_links.remove(link)

    # Fixes links in alert mails
    if generated_mail == 'alert':
        for link in trackable_links:
            if 'sip.lex' in link and '#' in link:
                base_part = link.split('?')[0]
                tracking_part = link.split('?')[1].split('#')[0]
                asset_part = link.split('?')[1].split('#')[1]
                if '?p=' in link:
                    filter_part = link.split('?')[2]
                    new_link = f'{base_part}#{asset_part}?{filter_part}&{tracking_part}'
                else:
                    new_link = f'{base_part}#{asset_part}?{tracking_part}'
                if '&elqTrack=true' not in new_link:
                    new_link = new_link + '&elqTrack=true'
                mail_html = mail_html.replace(link, new_link + '"')

    # Swaps file storage links to unbranded SSL
    mail_html = mail_html.replace(
        'http://images.go.wolterskluwer.com', 'https://img06.en25.com')

    return mail_html


'''
=================================================================================
                                Main program flow
=================================================================================
'''


def mail_constructor(country, campaign=False):
    '''
    Builds .mjml and .html files with eloqua-linked images, correct tracking scripts and pre-header
    Returns html code
    '''

    # Create global source_country and load json file with naming convention
    country_naming_setter(country)

    # Asks user to firstly upload images to Eloqua
    print(
        f'\n{Fore.YELLOW}» {Fore.WHITE}Please add email folder with',
        f'{Fore.YELLOW}Images, HTML, MJML{Fore.WHITE} to Incomes folder.',
        f'\n{Fore.WHITE}[Enter] to continue when finished.', end='')
    input(' ')

    # Lets user choose package to construct
    while True:
        # Gets name and files but image_files with index 3
        folder_name, html_files, mjml_files, image_files = package_chooser()
        if not folder_name:
            return False
        if not html_files and not mjml_files:
            print(
                f'{ERROR}Chosen package got neither HTML nor MJML file!')
        else:
            break

    '''
    =================================================== Get HTML & MJML
    '''

    html = ''
    if html_files:
        with open(file('package_file', file_name=html_files[0], folder_name=folder_name), 'r', encoding='utf-8') as f:
            html = f.read()
        # Builds list of to-be-swapped images in html file
        images = re.compile(r'src="(.*?)"', re.UNICODE)
        linkable_images_html = images.findall(html)
        linkable_images_html = list(set(linkable_images_html))
        linkable_images_html = [
            image for image in linkable_images_html if 'http' not in image]

    mjml = ''
    if mjml_files:
        with open(file('package_file', file_name=mjml_files[0], folder_name=folder_name), 'r', encoding='utf-8') as f:
            mjml = f.read()
        # Builds list of to-be-swapped images in mjml file
        linkable_images_mjml = images.findall(mjml)
        linkable_images_mjml = list(set(linkable_images_mjml))
        linkable_images_mjml = [
            image for image in linkable_images_mjml if 'http' not in image]

    '''
    =================================================== Image getter
    '''

    # Uploads each image and adds swaps relative link to url in code
    for image_name in image_files:
        print(f'\n   {Fore.YELLOW}› {Fore.WHITE}Adding {image_name} to', end='')
        image = {'file': open(file('package_file',
                                   file_name=image_name,
                                   folder_name=folder_name), 'rb')}
        image_link = api.eloqua_post_image(image)

        if html_files:
            for relative_link in linkable_images_html:
                if image_name in relative_link:
                    html = html.replace(relative_link, image_link)
                    print(f'{Fore.GREEN} › {Fore.WHITE}HTML',
                          end='', flush=True)
                    break

        if mjml_files:
            for relative_link in linkable_images_mjml:
                if image_name in relative_link:
                    relative_link = (relative_link.split('/'))[-1]
                    if '../Gfx/' in mjml:
                        mjml = mjml.replace(
                            '../Gfx/' + relative_link, image_link)
                    else:
                        mjml = mjml.replace(relative_link, image_link)
                    print(f'{Fore.GREEN} › {Fore.WHITE}MJML',
                          end='', flush=True)
                    break

    print(f'\n{Fore.WHITE}» {SUCCESS}Images uploaded and added to e-mail')

    '''
    =================================================== Placeholder links
    '''

    utm_track = re.compile(r'((\?|&)(kampania|utm).*?)(?=(#|"))', re.UNICODE)
    placeholder_link = naming[source_country]['mail']['placeholder_link']
    placeholder_regex = re.compile(placeholder_link, re.UNICODE)

    if html_files and placeholder_regex.findall(html) or mjml_files and placeholder_regex.findall(mjml):
        # If we have URL of the main Eloqua LP
        if campaign and campaign != 'linkless':
            if html_files:
                html = placeholder_regex.sub(campaign, html)
            if mjml_files:
                mjml = placeholder_regex.sub(campaign, mjml)
        else:  # If we need to get the URL from the user
            while True:
                print(f'\n{Fore.YELLOW}»{Fore.WHITE} Write or copypaste',
                      f'{Fore.YELLOW}untracked link for e-mail {Fore.WHITE}and click [Enter] or [S]kip')
                main_url = input(' ')
                if not main_url:
                    main_url = pyperclip.paste()
                if main_url == 's':  # If skipped
                    break
                elif utm_track.findall(main_url + '"'):
                    print(f'{ERROR}Entered value should not have tracking queries!')
                    continue
                elif main_url.startswith('http') or main_url.startswith('www'):
                    if html_files:
                        html = placeholder_regex.sub(main_url, html)
                    if mjml_files:
                        mjml = placeholder_regex.sub(main_url, mjml)
                    break
                else:
                    print(f'{ERROR}Entered value is not valid link!')

    '''
    =================================================== Track URL
    '''

    # Gets new UTM tracking
    while True:
        print(f'\n{Fore.YELLOW}»{Fore.WHITE} Write or copypaste',
              f'{Fore.YELLOW}UTM tracking script{Fore.WHITE} and click [Enter] or [S]kip')
        utm = input(' ')
        if not utm:
            utm = pyperclip.paste()
            if utm_track.findall(utm + '"'):
                break
        if utm.lower() == 's':
            break
        if utm_track.findall(utm + '"'):
            break
        print(f'{ERROR}Copied code is not correct UTM tracking script')

    # Gathers all links in HTML
    links = re.compile(r'href=(".*?")', re.UNICODE)
    if html_files:
        trackable_links = links.findall(html)
    elif mjml_files:
        trackable_links = links.findall(mjml)
    trackable_links = list(set(trackable_links))

    # Removes untrackable links
    for link in trackable_links[:]:
        if not link or 'googleapis' in link or 'emailfield' in link:
            trackable_links.remove(link)

    if html_files:
        html = link_manipulator(html, trackable_links, utm)

    if mjml_files:
        mjml = link_manipulator(mjml, trackable_links, utm)

    '''
    =================================================== Swap pre-header
    '''

    # Gets pre-header from user
    if (html_files and re.search('Pre-header', html)) or (mjml_files and re.search('Pre-header', mjml)):
        while True:
            print(
                f'\n{Fore.YELLOW}»{Fore.WHITE} Write or copypaste desired',
                f'{Fore.YELLOW}pre-header{Fore.WHITE} text and click [Enter] or [S]kip')
            preheader = input(' ')
            if not preheader:
                preheader = pyperclip.paste()
            if preheader == 's':
                preheader = '<!--pre-start-->pre-header<!--pre-end-->'
                break
            elif not preheader:
                print(f'\n{ERROR}Pre-header can not be blank')
            elif len(preheader) > 140:
                print(f'\n{ERROR}Pre-header is over 140 characters long')
            else:
                preheader = '<!--pre-start-->' + preheader + '<!--pre-end-->'
                break

        if html_files and preheader.lower() != 's' and re.search('Pre-header', html):
            html = html.replace('Pre-header', preheader)
            reminder_html = html
            html = html.replace('<!--pre-start-->', '')\
                       .replace('<!--pre-end-->', '')

        if mjml_files and preheader.lower() != 's' and re.search('Pre-header', mjml):
            mjml = mjml.replace('>Pre-header', '>' + preheader)\
                       .replace('<!--pre-start-->', '')\
                       .replace('<!--pre-end-->', '')

    '''
    =================================================== Save MJML to Outcomes
    '''

    if html_files:
        with open(file('mail_html', file_name=folder_name), 'w', encoding='utf-8') as f:
            f.write(html)

    if mjml_files:
        with open(file('mail_mjml', file_name=folder_name), 'w', encoding='utf-8') as f:
            f.write(mjml)

    print(f'\n{SUCCESS}Code saved to Outcomes folder')

    if campaign:
        return html

    output_method(html, mjml)

    # Asks user about reminder e-mail creation
    print(f'\n{Fore.YELLOW}» {Fore.WHITE}Do you want to {Fore.YELLOW}create reminder{Fore.WHITE} Email?',
          f'{Fore.WHITE}({YES}/{NO}):', end=' ')
    choice = input('')
    if choice.lower() == 'y':
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
                reminder_preheader, reminder_html)
            reminder_html = reminder_html.replace('<!--pre-start-->', '')\
                                         .replace('<!--pre-end-->', '')
        else:
            reminder_html = html
        output_method(reminder_html)

    # Asks user if he would like to repeat
    print(f'\n{Fore.YELLOW}» {Fore.WHITE}Do you want to {Fore.YELLOW}construct another Email{Fore.WHITE}?',
          f'{Fore.WHITE}({YES}/{NO}):', end=' ')
    choice = input('')
    if choice.lower() == 'y':
        print(
            f'\n{Fore.GREEN}-----------------------------------------------------------------------------')
        mail_constructor(country)

    return html
