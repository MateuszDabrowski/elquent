#!/usr/bin/env python3.6
# -*- coding: utf8 -*-
# pylint: disable=W0702

'''
ELQuent.certificate
Automated certificate creator using database.csv and template.pdf

Mateusz Dąbrowski
github.com/MateuszDabrowski
linkedin.com/in/mateusz-dabrowski-marketing/
'''

# Python imports
import os
import io
import re
import sys
import csv
import json
import webbrowser
from datetime import datetime
import PyPDF2
from colorama import Fore, Style, init
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor

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
                            File Path Getters
=================================================================================
'''


def file(file_path, name=''):
    '''
    Returns file path to template files
    '''

    def find_data_file(filename, directory):
        '''
        Returns correct file path for both script and frozen app
        '''
        if directory == 'api':  # For reading api files
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

    file_paths = {
        'naming': find_data_file('naming.json', directory='api'),
        'database': find_data_file('database.csv', directory='incomes'),
        'template': find_data_file('template.pdf', directory='incomes'),
        'certified': find_data_file('certified_users.csv', directory='outcomes'),
        'certificate': find_data_file(f'Certificate-{name}', directory='outcomes')
    }

    return file_paths.get(file_path)


'''
=================================================================================
                            Helper Functions
=================================================================================
'''


def get_template():
    '''
    Loads template.pdf
    Returns:
    » template_file: PyPDF2 template.pdf from incomes folder
    » template_width: integer
    » template_height: integer
    '''
    # Load template.pdf
    template_file = PyPDF2.PdfFileReader(open(file('template'), 'rb'))
    template_width = int(template_file.getPage(0).mediaBox[2])
    template_height = int(template_file.getPage(0).mediaBox[3])

    return (template_file, template_width, template_height)


def set_font():
    '''
    Returns:
    » font_type: string with font name
    » font_size: integer with font size
    '''
    # Font chooser
    font_type = ''
    while font_type not in ['1', '2', '3', '4']:
        print(
            f'\n{Fore.GREEN}Please select font you want to use:'
            f'\n{Fore.WHITE}[{Fore.YELLOW}1{Fore.WHITE}]\t» [{Fore.YELLOW}FiraSans{Fore.WHITE}]'
            f'\n{Fore.WHITE}[{Fore.YELLOW}2{Fore.WHITE}]\t» [{Fore.YELLOW}FiraSans Italic{Fore.WHITE}]'
            f'\n{Fore.WHITE}[{Fore.YELLOW}3{Fore.WHITE}]\t» [{Fore.YELLOW}FiraSans Bold{Fore.WHITE}]'
            f'\n{Fore.WHITE}[{Fore.YELLOW}4{Fore.WHITE}]\t» [{Fore.YELLOW}FiraSans Bold Italic{Fore.WHITE}]'
            f'\n{Fore.YELLOW}Enter number associated with chosen font type:', end=' '
        )
        font_type = input(' ')
        if font_type not in ['1', '2', '3', '4']:
            print(f'{Fore.RED}Entered value is not valid!')
    font_type = ['FiraSans', 'FiraSans I',
                 'FiraSans B', 'FiraSans BI'][int(font_type) - 1]

    # Page size chooser
    print(f'\n{Fore.YELLOW}Please write font size of the text:', end=' ')
    font_size = input(' ')

    return (font_type, int(font_size))


def set_color():
    '''
    Returns:
    » font_color: string containing hex color
    '''
    # Font chooser
    while True:
        print(
            f'\n{Fore.YELLOW}Please enter hex value of a color (example: #007ac3):', end='')
        font_color = input(' ')
        hex_match = re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', font_color)
        if hex_match:
            break
        else:
            print(f'{Fore.RED}Entered value is not valid!')

    return font_color


def create_name_file(width, height, font, size, color, first_name, last_name, text_height=''):
    '''
    Requires:
    » width, height, size: integers
    » font, first_name, last_name: strings
    Returns name_watermark_pdf with chosen string over transparent canvas
    '''
    packet = io.BytesIO()

    # Page size chooser
    if not text_height:
        print(
            f'\n{Fore.YELLOW}Please write y-axis value for first name (middle: {height/2}):', end=' ')
        text_height = input(' ')
        text_height = int(float(text_height))

    # Create a new PDF with Reportlab
    name_watermark = canvas.Canvas(packet)
    name_watermark.setPageSize((width, height))
    name_watermark.setFont(font, size)
    name_watermark.setFillColor(HexColor(color))
    name_watermark.drawCentredString(width/2,
                                     text_height,
                                     first_name)
    name_watermark.drawCentredString(width/2,
                                     text_height - size,
                                     last_name)
    name_watermark.showPage()
    name_watermark.save()

    # Move to the beginning of the StringIO buffer
    packet.seek(0)
    name_watermark_pdf = PyPDF2.PdfFileReader(packet)

    return (name_watermark_pdf, text_height)


def create_cert_file(template_pdf, name_pdf, first_name, last_name):
    '''
    Requires:
    » template_pdf & name_pdf: PyPDF2 objects
    » first_name, last_name: strings
    Returns file path
    '''
    output = PyPDF2.PdfFileWriter()

    accent_dict = {
        'ą': 'a', 'ę': 'e', 'ó': 'o', 'ś': 's', 'ł': 'l',
        'ż': 'z', 'ź': 'z', 'ć': 'c', 'ń': 'n'
    }

    # Gets date for file naming
    today = str(datetime.now())[:10]

    # Overlays first page of name_pdf over first page of template_pdf
    page = template_pdf.getPage(0)
    page.mergePage(name_pdf.getPage(0))
    output.addPage(page)

    deaccented_first_name = ''
    for char in first_name.lower():
        if char in accent_dict.keys():
            deaccented_first_name += accent_dict.get('char', '_')
        else:
            deaccented_first_name += char

    deaccented_last_name = ''
    for char in last_name.lower():
        if char in accent_dict.keys():
            deaccented_last_name += accent_dict.get(char, '_')
        else:
            deaccented_last_name += char

    # Saves filled certificate to Outcomes folder
    outputStream = open(file(
        'certificate',
        name=f'{today}-{deaccented_first_name}-{deaccented_last_name}.pdf'), "wb")
    output.write(outputStream)
    outputStream.close()

    return file('certificate',
                name=f'{today}-{deaccented_first_name}-{deaccented_last_name}.pdf')


'''
=================================================================================
                            Main Program Flow
=================================================================================
'''


def cert_constructor(country):
    '''
    Requires:
    » database.csv: csv with Email Address, First Name, Last Name of certified users
    » template.pdf: pdf on which the First Name and Last Name should be printed
    » Fira Sans: installed font: https://fonts.google.com/specimen/Fira+Sans
    '''

    try:  # Fira Sans font registration
        pdfmetrics.registerFont(
            TTFont('FiraSans', 'FiraSans-Regular.ttf'))
        pdfmetrics.registerFont(
            TTFont('FiraSans I', 'FiraSans-Italic.ttf'))
        pdfmetrics.registerFont(
            TTFont('FiraSans B', 'FiraSans-SemiBold.ttf'))
        pdfmetrics.registerFont(
            TTFont('FiraSans BI', 'FiraSans-SemiBoldItalic.ttf'))
    except:  # Triggered by lack of above fonts in default folder
        print(f'\n{ERROR}Fira Sans fonts are not installed!'
              f'{Fore.WHITE}» Install from: https://fonts.google.com/specimen/Fira+Sans')
        return

    # Create global source_country and load json file with naming convention
    country_naming_setter(country)

    # Asks user to firstly add required files
    while True:
        print(
            f'\n{Fore.GREEN}Please add to Incomes folder:',
            f'\n{Fore.YELLOW}» {Fore.WHITE}database.csv comma-delimited with headers',
            f'\n{Fore.WHITE}   [{Fore.YELLOW}Email Address, First Name, Last Name{Fore.WHITE}]',
            f'\n{Fore.YELLOW}» {Fore.WHITE}template.pdf',
            f'\n{Fore.WHITE}[{Fore.YELLOW}Enter{Fore.WHITE}] to continue when finished '
            f'{Fore.WHITE}or [{Fore.YELLOW}Q{Fore.WHITE}] to quit.', end='')
        menu = input(' ')
        if menu.lower() == 'q':
            return
        elif os.path.isfile(file('template')) and os.path.isfile(file('database')):
            break
        else:
            print(f'{ERROR}Cannot find files in Incomes folder!')

    # Gets font type and font size from user input
    font, size = set_font()
    color = set_color()

    # Create sample certificate to test settings
    while True:
        template_pdf, width, height = get_template()
        name_pdf, text_position = create_name_file(
            width, height, font, size, color, 'Mateusz', 'Dąbrowski')
        cert_path = create_cert_file(
            template_pdf, name_pdf, 'Mateusz', 'Dąbrowski')
        print(f'\n{Fore.YELLOW}» {Fore.WHITE}Check sample certificate for Mateusz Dąbrowski in Outcomes folder!',
              f'\n{Fore.WHITE}  Continue with current settings? ({YES}/{NO}):', end=' ')
        webbrowser.open(f'file://{cert_path}', new=2, autoraise=False)
        choice = input('')
        if choice.lower() == 'y':
            break
        else:
            while choice not in ['1', '2']:
                print(
                    f'\n{Fore.GREEN}Please select what you want to change:'
                    f'\n{Fore.WHITE}[{Fore.YELLOW}1{Fore.WHITE}]\t» [{Fore.YELLOW}Font type or size{Fore.WHITE}]'
                    f'\n{Fore.WHITE}[{Fore.YELLOW}2{Fore.WHITE}]\t» [{Fore.YELLOW}Placement of the name{Fore.WHITE}]'
                    f'\n{Fore.WHITE}[{Fore.YELLOW}Q{Fore.WHITE}]\t» [{Fore.YELLOW}Quit creator{Fore.WHITE}]'
                )
                choice = input(' ')
                if choice.lower() == 'q':
                    return
                elif choice == '1':
                    font, size = set_font()
                elif choice == '2':
                    break

    # Loads all users from database.csv
    while True:
        with open(file('database'), 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            users = list(reader)

        # Checks if csv has correct number of rows
        if len(users[0]) == 3 and '@' in users[1][0]:
            break
        else:
            print(f'{ERROR}Incorrect structure of database.csv! '
                  f'{Fore.YELLOW}Add csv with three columns [Email Address, First Name, Last Name] and click [Enter]')
            input('')

    # Create structure for csv output
    certified_users = [['Source_Country', 'Email Address',
                        'First Name', 'Last Name', 'Certificate']]
    print(f'\n{Fore.WHITE}Creating certificates:', end=' ')
    for user in users[1:]:
        email, first_name, last_name = (user[0], user[1], user[2])

        # Builds PyPDF2 template object and gets its size for correct watermark placing
        template_pdf, width, height = get_template()

        # Creates name watermark with given data
        name_pdf, _ = create_name_file(
            width, height, font, size, color, first_name, last_name, text_position)

        # Creates certificate for the user
        cert_path = create_cert_file(
            template_pdf, name_pdf, first_name, last_name)

        # Builds list for outcome .csv
        certified_users.append(
            [source_country, email, first_name, last_name, cert_path])

        print(f'{Fore.GREEN}|', end='', flush=True)

    print(f'\n\n{SUCCESS}{len(certified_users)-1} '
          f'{Fore.WHITE}certificates created and saved to Outcomes folder!')

    # Let user decide whether certificates should be uploaded to Eloqua
    choice = ''
    while choice.lower() not in ['y', 'n']:
        print(
            f'\n{Fore.YELLOW}» {Fore.WHITE}Upload to Eloqua? ({YES}/{NO}):', end=' ')
        choice = input('')
        if choice.lower() == 'n':
            # Create a csv with file paths if no upload
            with open(file('certified'), 'w', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerows(certified_users)
            print(f'\n\n{SUCCESS} contact upload file saved to Outcomes folder!')

            return
        elif choice.lower() == 'y':
            break

    # Upload all certificates to Eloqua
    upload_list = [['Source_Country', 'Email Address',
                    'First Name', 'Last Name', 'Certificate ID']]
    for user in certified_users[1:]:
        print(f'\n   {Fore.YELLOW}› {Fore.WHITE}Adding '
              f'{Fore.WHITE}{user[2]} {user[3]} certificate to', end='')
        cert_path = user[4]
        certificate = {'file': open(cert_path, 'rb')}
        cert_link = api.eloqua_post_file(certificate)

        # Builds list for outcome .csv
        user[4] = cert_link
        upload_list.append(user)
        print(f'{Fore.GREEN} › {Fore.WHITE}CSV', end='', flush=True)

    # Create a csv with certificate links for upload
    with open(file('certified'), 'w', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(upload_list)

    print(f'\n\n{SUCCESS}{len(certified_users)-1} certificates uploaded to Eloqua!'
          f'\n{Fore.WHITE}Contact upload .csv file saved to Outcomes folder!')
