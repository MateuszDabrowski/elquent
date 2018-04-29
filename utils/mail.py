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
import requests
import encodings
import pyperclip
from colorama import Fore, init

# ELQuent imports
import utils.api.api as api

# Initialize colorama
init(autoreset=True)

# Predefined messege elements
ERROR = f'{Fore.WHITE}[{Fore.RED}ERROR{Fore.WHITE}] {Fore.YELLOW}'
SUCCESS = f'{Fore.WHITE}[{Fore.GREEN}SUCCESS{Fore.WHITE}] '

'''
=================================================================================
                            File Path Getter
=================================================================================
'''


def file(file_path, file_name='', folder_name=''):
    '''
    Returns file path to template files
    '''

    def find_data_file(filename, dir='incomes', folder_name=''):
        '''
        Returns correct file path for both script and frozen app
        '''
        if dir == 'main':  # Files in main directory
            if getattr(sys, 'frozen', False):
                datadir = os.path.dirname(sys.executable)
            else:
                datadir = os.path.dirname(os.path.dirname(__file__))
            return os.path.join(datadir, filename)
        elif dir == 'incomes':  # For reading user files
            if getattr(sys, 'frozen', False):
                datadir = os.path.dirname(sys.executable)
            else:
                datadir = os.path.dirname(os.path.dirname(__file__))
            return os.path.join(datadir, dir, filename)
        elif dir == 'outcomes':  # For writing outcome files
            if getattr(sys, 'frozen', False):
                datadir = os.path.dirname(sys.executable)
            else:
                datadir = os.path.dirname(os.path.dirname(__file__))
            return os.path.join(datadir, dir, filename)
        elif dir == 'package':  # For reading package files
            if getattr(sys, 'frozen', False):
                datadir = os.path.dirname(sys.executable)
            else:
                datadir = os.path.dirname(os.path.dirname(__file__))
            return os.path.join(datadir, 'incomes', folder_name, filename)

    file_paths = {
        'incomes': find_data_file('incomes', dir='main'),
        'package': find_data_file(f'{file_name}'),
        'package_file': find_data_file(f'{file_name}', dir='package', folder_name=folder_name),
        'mail_html': find_data_file(f'WK{source_country}_{file_name}.txt', dir='outcomes'),
        'mail_mjml': find_data_file(f'WK{source_country}_{file_name}.mjml', dir='outcomes')
    }

    return file_paths.get(file_path)


'''
=================================================================================
                                Code Output Helper
=================================================================================
'''


def output_method(html_code='', mjml_code=''):
    '''
    Allows user choose how the program should output the results
    '''
    print(
        f'\n{Fore.GREEN}New code should be:',
        f'\n{Fore.WHITE}[{Fore.YELLOW}0{Fore.WHITE}]\t» [{Fore.YELLOW}FILE{Fore.WHITE}] Only saved to Outcomes folder')
    if html_code:
        print(
            f'{Fore.WHITE}[{Fore.YELLOW}1{Fore.WHITE}]\t» [{Fore.YELLOW}HTML{Fore.WHITE}] Copied to clipboard as HTML for pasting [CTRL+V]')
    if mjml_code:
        print(
            f'{Fore.WHITE}[{Fore.YELLOW}2{Fore.WHITE}]\t» [{Fore.YELLOW}MJML{Fore.WHITE}] Copied to clipboard as MJML for pasting [CTRL+V]')
    print(
        f'{Fore.WHITE}[{Fore.YELLOW}3{Fore.WHITE}]\t» [{Fore.YELLOW}CREATE{Fore.WHITE}] Uploaded to Eloqua as a new E-mail',
        f'\n{Fore.WHITE}[{Fore.YELLOW}4{Fore.WHITE}]\t» [{Fore.YELLOW}UPDATE{Fore.WHITE}] Uploaded to Eloqua as update to existing E-mail')
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
                f'\n{Fore.WHITE}[{Fore.YELLOW}ID{Fore.WHITE}]{Fore.YELLOW} » Write or paste name of the E-mail:')
            name = api.eloqua_asset_name()
            api.eloqua_create_email(name, html_code)
            break
        elif choice == '4':
            print(
                f'\n{Fore.WHITE}[{Fore.YELLOW}ID{Fore.WHITE}]{Fore.YELLOW} » Write or paste ID of the E-mail to update:')
            email_id = input(' ')
            api.eloqua_update_email(email_id, html_code)
            break
        else:
            print(f'{ERROR}Entered value does not belong to any utility!')
            choice = ''


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
        files = os.listdir(file('package', file_name=folder))
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
    print(f'\n{Fore.WHITE}[{Fore.YELLOW}Q{Fore.WHITE}] {Fore.WHITE}Quit')
    print(f'{Fore.YELLOW}Enter number associated with chosen package:', end='')
    choice = input(' ')

    # Allows user to pick which package should be build
    while True:
        if not choice:
            print(
                f'{Fore.YELLOW}Enter number associated with chosen package:', end='')
            choice = input(' ')
        if choice.lower() == 'q':
            print(f'\n{Fore.GREEN}Ahoj!')
            raise SystemExit
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
    return (folder_name, packages.get(folder_name).get('html'), packages.get(folder_name).get('mjml'), packages.get(folder_name).get('img'))


'''
=================================================================================
                                Main program flow
=================================================================================
'''


def mail_constructor(country):
    '''
    Builds .mjml and .html files with eloqua-linked images, correct tracking scripts and pre-header
    Returns html code
    '''
    # Creates global source_country from main module
    global source_country
    source_country = country

    # Asks user to firstly upload images to Eloqua
    print(
        f'\n{Fore.YELLOW}» {Fore.WHITE}Please add email folder with {Fore.YELLOW}Images, HTML, MJML{Fore.WHITE} to Incomes folder.',
        f'\n{Fore.WHITE}[Enter] to continue when finished.', end='')
    input(' ')

    # Lets user choose package to construct
    while True:
        # Gets name and files but image_files with index 3
        folder_name, html_files, mjml_files = package_chooser()[0:3]
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

    mjml = ''
    if mjml_files:
        with open(file('package_file', file_name=mjml_files[0], folder_name=folder_name), 'r', encoding='utf-8') as f:
            mjml = f.read()

    '''
    =================================================== Image getter
    '''

    # Asks user to firstly upload images to Eloqua
    print(
        f'\n{Fore.YELLOW}»{Fore.WHITE} Please upload {Fore.YELLOW}{folder_name}{Fore.WHITE} images to Eloqua.',
        f'\n{Fore.WHITE}[Enter] to continue when finished.', end='')
    input(' ')

    print(f'\n{Fore.GREEN}Adding image links from Eloqua:', end='')
    # Gets list of images in package
    images = re.compile(r'src="(.*?)"', re.UNICODE)
    if html_files:
        # Builds list of images that should be swapped
        linkable_images_html = images.findall(html)
        linkable_images_html = list(set(linkable_images_html))
        linkable_images_html = [
            image for image in linkable_images_html if 'http' not in image]

        print(f'\n{Fore.WHITE}» HTML ', end='')
        # Gets image link from Eloqua and adds it to the code
        for image in linkable_images_html:
            image_link = api.eloqua_get_image(image)
            html = html.replace(image, image_link)
            print(f'{Fore.GREEN}|', end='', flush=True)

    if mjml_files:
        # Builds list of images that should be swapped
        linkable_images_mjml = images.findall(mjml)
        linkable_images_mjml = list(set(linkable_images_mjml))
        linkable_images_mjml = [
            image for image in linkable_images_mjml if 'http' not in image]

        print(f'\n{Fore.WHITE}» MJML ', end='')
        # Gets image link from Eloqua and adds it to the code
        for image in linkable_images_mjml:
            image = (image.split('/'))[-1]
            image_link = api.eloqua_get_image(image)
            mjml = mjml.replace('../Gfx/' + image, image_link)
            print(f'{Fore.GREEN}|', end='', flush=True)

    '''
    =================================================== Track URL
    '''

    # Gets new UTM tracking
    utm_track = re.compile(r'((\?|&)(kampania|utm).*?)(?=(#|"))', re.UNICODE)
    while True:
        print(
            f'\n\n{Fore.YELLOW}»{Fore.WHITE} Write or paste new {Fore.YELLOW}UTM tracking script{Fore.WHITE} and click [Enter] or [S]kip')
        utm = input(' ')
        if utm.lower() == 's':
            break
        if utm_track.findall(utm + '"'):
            break
        print(
            f'{ERROR}Copied code is not correct UTM tracking script')

    # Gathers all links in HTML
    links = re.compile(r'href=(".*?")', re.UNICODE)
    if html_files:
        trackable_links = links.findall(html)
    elif mjml_files:
        trackable_links = links.findall(mjml)
    trackable_links = list(set(trackable_links))

    # Removes untrackable links
    for link in trackable_links[:]:
        if 'googleapis' in link or 'emailfield' in link:
            trackable_links.remove(link)

    # Appending UTM to all trackable_links in HTML
    if html_files and utm.lower() != 's':
        for link in trackable_links:
            if '?' in link:
                html = html.replace(link, (link[:-1] + '&' + utm[1:] + '"'))
            else:
                html = html.replace(link, (link[:-1] + utm + '"'))
    if mjml_files and utm.lower() != 's':
        for link in trackable_links:
            if '?' in link:
                mjml = mjml.replace(link, (link[:-1] + '&' + utm[1:] + '"'))
            else:
                mjml = mjml.replace(link, (link[:-1] + utm + '"'))

    '''
    =================================================== Swap pre-header
    '''

    # Gets pre-header from user
    if (html_files and re.search('Pre-header', html)) or (mjml_files and re.search('Pre-header', mjml)):
        print(
            f'\n{Fore.YELLOW}»{Fore.WHITE} Write or paste desired {Fore.YELLOW}pre-header{Fore.WHITE} text and click [Enter] or [S]kip')
        preheader = input(' ')

        if html_files and preheader.lower() != 's' and re.search('Pre-header', html):
            html = html.replace('Pre-header', preheader)

        if mjml_files and preheader.lower() != 's' and re.search('Pre-header', mjml):
            mjml = mjml.replace('Pre-header', preheader)

    '''
    =================================================== Save MJML to Outcomes
    '''

    if html_files:
        with open(file('mail_html', file_name=folder_name), 'w', encoding='utf-8') as f:
            f.write(html)

    if mjml_files:
        with open(file('mail_mjml', file_name=folder_name), 'w', encoding='utf-8') as f:
            f.write(mjml)

    print(
        f'\n{SUCCESS}Code saved to Outcomes folder')

    output_method(html, mjml)

    # Asks user if he would like to repeat
    print(f'\n{Fore.YELLOW}» {Fore.WHITE}Do you want to construct another Email? ({Fore.GREEN}y{Fore.WHITE}/{Fore.RED}n{Fore.WHITE})', end='')
    choice = input(' ')
    if choice.lower() == 'y':
        mail_constructor(country)

    return
