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
ERROR = f'{Fore.RED}[ERROR] {Fore.YELLOW}'

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
        'mail_html': find_data_file(f'WK{source_country}_{file_name}.html', dir='outcomes'),
        'mail_mjml': find_data_file(f'WK{source_country}_{file_name}.mjml', dir='outcomes')
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
            print(f'{Fore.RED}Please enter numeric value!')
            choice = ''
            continue
        if 0 <= choice < len(folders):
            break
        else:
            print(f'{Fore.RED}Entered value does not belong to any package!')
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
        f'\n{Fore.YELLOW}» Please add email folder with {Fore.WHITE}Images, HTML, MJML{Fore.YELLOW} to Incomes folder.\n{Fore.WHITE}[Enter] to continue when finished.', end='')
    input(' ')

    # Lets user choose package to construct
    while True:
        folder_name, html_files, mjml_files, image_files = package_chooser()
        if not html_files and not mjml_files:
            print(f'{Fore.RED}Chosen package got neither HTML nor MJML file!')
        else:
            break

    '''
    =================================================== Get HTML & MJML
    '''

    if html_files:
        with open(file('package_file', file_name=html_files[0], folder_name=folder_name), 'r', encoding='utf-8') as f:
            html = f.read()

    if mjml_files:
        with open(file('package_file', file_name=mjml_files[0], folder_name=folder_name), 'r', encoding='utf-8') as f:
            mjml = f.read()

    '''
    =================================================== Image getter
    '''

    # Asks user to firstly upload images to Eloqua
    print(
        f'\n{Fore.YELLOW}» Please upload {Fore.WHITE}{folder_name}{Fore.YELLOW} images to Eloqua.\n{Fore.WHITE}[Enter] to continue when finished.', end='')
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
            f'\n\n{Fore.WHITE}» Write or copy new {Fore.YELLOW}UTM tracking script{Fore.WHITE} and click [Enter]')
        utm = input(' ')
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
    if html_files:
        for link in trackable_links:
            if '?' in link:
                html = html.replace(link, (link[:-1] + '&' + utm[1:] + '"'))
            else:
                html = html.replace(link, (link[:-1] + utm + '"'))
    if mjml_files:
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
            f'\n{Fore.WHITE}» Write or copy desired {Fore.YELLOW}pre-header{Fore.WHITE} text and click [Enter]')
        preheader = input(' ')

        if html_files and re.search('Pre-header', html):
            html = html.replace('Pre-header', preheader)

        if mjml_files and re.search('Pre-header', mjml):
            mjml = mjml.replace('Pre-header', preheader)

    '''
    =================================================== Save MJML to Outcomes
    '''

    if html_files:
        with open(file('mail_html', file_name=folder_name), 'w', encoding='utf-8') as f:
            f.write(html)
        pyperclip.copy(html)

    if mjml_files:
        with open(file('mail_mjml', file_name=folder_name), 'w', encoding='utf-8') as f:
            f.write(mjml)

    print(
        f'\n{Fore.GREEN}» You can now paste constructed Email to Eloqua [CTRL+V].',
        f'\n{Fore.WHITE}  (It is also saved to Outcomes folder)')

    # Asks user if he would like to repeat
    print(f'\n{Fore.GREEN}Do you want to construct another Email? (Y/N)', end='')
    choice = input(' ')
    if choice.lower() == 'y':
        mail_constructor(country)

    return
