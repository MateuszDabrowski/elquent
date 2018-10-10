#!/usr/bin/env python3.6
# -*- coding: utf8 -*-

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
import sys
import csv
import json
import PyPDF2
from colorama import Fore, Style, init
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ELQuent imports
import utils.api.api as api

# Initialize colorama
init(autoreset=True)

# Globals
naming = None
source_country = None

# Fira Sans fonts
pdfmetrics.registerFont(TTFont('FiraSans', 'FiraSans-Regular.ttf'))
pdfmetrics.registerFont(TTFont('FiraSans I', 'FiraSans-Italic.ttf'))
pdfmetrics.registerFont(TTFont('FiraSans B', 'FiraSans-SemiBold.ttf'))
pdfmetrics.registerFont(TTFont('FiraSans BI', 'FiraSans-SemiBoldItalic.ttf'))

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
        'certificate': find_data_file(f'Certificate-{name}.pdf', directory='outcomes')
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
    while int(font_type) not in range(1, 4):
        print(
            f'\n{Fore.GREEN}Please select font you want to use:'
            f'\n{Fore.WHITE}[{Fore.YELLOW}1{Fore.WHITE}]\t» [{Fore.YELLOW}FiraSans{Fore.WHITE}]'
            f'\n{Fore.WHITE}[{Fore.YELLOW}2{Fore.WHITE}]\t» [{Fore.YELLOW}FiraSans Italic{Fore.WHITE}]'
            f'\n{Fore.WHITE}[{Fore.YELLOW}3{Fore.WHITE}]\t» [{Fore.YELLOW}FiraSans Bold{Fore.WHITE}]'
            f'\n{Fore.WHITE}[{Fore.YELLOW}4{Fore.WHITE}]\t» [{Fore.YELLOW}FiraSans Bold Italic{Fore.WHITE}]'
        )
        font_type = input(' ')
        if int(font_type) not in range(1, 4):
            print(f'{Fore.RED}Entered value is not valid!')
    font_type = ['FiraSans', 'FiraSans I',
                 'FiraSans B', 'FiraSans BI'][int(font_type) - 1]

    # Page size chooser
    print(f'{Fore.YELLOW}Please write font size of the text:', end=' ')
    font_size = input(' ')

    return (font_type, font_size)


def create_name_file(width, height, font, size, first_name, last_name):
    '''
    Requires:
    » width, height, size: integers
    » font, first_name, last_name: strings
    Returns name_watermark_pdf with chosen string over transparent canvas
    '''
    packet = io.BytesIO()

    # Page size chooser
    print(f'{Fore.YELLOW}Please write y-axis value for first name (middle: {height/2}):', end=' ')
    text_height = input(' ')
    text_height = int(text_height)

    # Create a new PDF with Reportlab
    name_watermark = canvas.Canvas(packet)
    name_watermark.setPageSize((width, height))
    name_watermark.setFont(font, size)
    name_watermark.drawCentredString(width/2,
                                     text_height,
                                     first_name)
    name_watermark.drawCentredString(width/2,
                                     text_height - size * 1.5,
                                     last_name)
    name_watermark.showPage()
    name_watermark.save()

    # Move to the beginning of the StringIO buffer
    packet.seek(0)
    name_watermark_pdf = PyPDF2.PdfFileReader(packet)

    return name_watermark_pdf


def create_cert_file(template_pdf, name_pdf, first_name, last_name):
    '''
    Requires:
    » template_pdf & name_pdf: PyPDF2 objects
    » first_name, last_name: strings
    Returns file path
    '''
    output = PyPDF2.PdfFileWriter()

    # Overlays first page of name_pdf over first page of template_pdf
    page = template_pdf.getPage(0)
    page.mergePage(name_pdf.getPage(0))
    output.addPage(page)

    # Saves filled certificate to Outcomes folder
    outputStream = open(
        file('certificate', name=f'{first_name}-{last_name}.pdf'), "wb")
    output.write(outputStream)
    outputStream.close()

    return file('certificate', name=f'{first_name}-{last_name}.pdf')


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

    # Create global source_country and load json file with naming convention
    country_naming_setter(country)

    # Asks user to firstly add required files
    while True:
        print(
            f'\n{Fore.WHITE}Please add to Incomes folder:',
            f'\n{Fore.WHITE}» {Fore.YELLOW}database.csv{Fore.WHITE} [Email Address, First Name, Last Name]',
            f'\n{Fore.WHITE}» {Fore.YELLOW}template.pdf',
            f'\n{Fore.WHITE}[Enter] to continue when finished or [Q] to quit.', end='')
        menu = input(' ')
        if menu.lower() == 'q':
            return
        elif os.path.isfile(file('template')) and os.path.isfile(file('database')):
            break
        else:
            print(f'{ERROR}Cannot find files in Incomes folder!')

    # Builds PyPDF2 template object and gets its size for correct watermark placing
    template_pdf, width, height = get_template()

    # Gets font type and font size from user input
    font, size = set_font()

    # Create sample certificate to test settings
    while True:
        name_pdf = create_name_file(
            width, height, font, size, 'Mateusz', 'Dąbrowski')
        create_cert_file(template_pdf, name_pdf, 'Mateusz', 'Dąbrowski')
        print(f'{SUCCESS}Saved sample certificate for Mateusz Dąbrowski in Outcomes folder!',
              f'\n{Fore.WHITE}Continue with current settings? ({YES}/{NO}):', end=' ')
        choice = input('')
        if choice.lower() == 'y':
            break
        else:
            while int(choice) not in range(1, 2):
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
    with open(file('database'), 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        users = list(reader)

    # TODO: basic .csv content validation

    certified_users = []
    for user in users:
        email, first_name, last_name = (user[0], user[1], user[2])

        # Creates name watermark with given data
        name_pdf = create_name_file(
            width, height, font, size, first_name, last_name)

        # Creates certificate for the user
        cert_path = create_cert_file(
            template_pdf, name_pdf, first_name, last_name)

    # TODO: Eloqua API pdf upload, url feedback, new .csv creation
        # header_row = ['Source_Country', 'Email Address', 'First Name', 'Last Name', 'WKCORP_Free_Field']
        # certified_user = [source_country] + user + [cert_url]
        # certified_users.append(certified_user)
