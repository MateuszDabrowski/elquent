#!/usr/bin/env python3.6
# -*- coding: utf8 -*-

'''
ELQuent.setup
Creates executable of ELQuent app

Mateusz Dąbrowski
github.com/MateuszDabrowski
linkedin.com/in/mateusz-dabrowski-marketing/
'''

from cx_Freeze import setup, Executable

buildOptions = dict(
    include_files=['README.md', 'LICENSE', 'utils', 'utils.json'],
    packages=['pyperclip', 'csv', 're', 'os', 'sys', 'pickle', 'requests', 'idna',
              'platform', 'colorama', 'json', 'multiprocessing', 'shutil', 'PyPDF2',
              'time', 'datetime', 'getpass', 'base64', 'webbrowser', 'reportlab']
)

base = 'Console'

executables = [
    Executable('elquent.py', base=base)
]

setup(name='ELQuent',
      version='1.8',
      description='Eloqua automation utility bundle',
      author='Mateusz Dąbrowski',
      url='https://github.com/MateuszDabrowski/',
      options=dict(build_exe=buildOptions),
      executables=executables)
