'''
ELQuent.setup
Creates executable of ELQuent app

Mateusz Dąbrowski
github.com/MateuszDabrowski
linkedin.com/in/mateusz-dabrowski-marketing/
'''

import os
from cx_Freeze import setup, Executable

if os.name == 'nt':  # Required on Windows to freeze Dash
    os.environ['TCL_LIBRARY'] = "C:\\Program Files (x86)\\Python35-32\\tcl\\tcl8.6"
    os.environ['TK_LIBRARY'] = "C:\\Program Files (x86)\\Python35-32\\tcl\\tk8.6"

buildOptions = dict(
    include_files=['README.md', 'LICENSE', 'utils', 'utils.json'],
    packages=['pyperclip', 'csv', 're', 'os', 'sys', 'pickle', 'requests', 'idna',
              'platform', 'colorama', 'json', 'multiprocessing', 'shutil'
              'time', 'datetime', 'getpass', 'base64', 'webbrowser']
)

base = 'Console'

executables = [
    Executable('elquent.py', base=base)
]

setup(name='ELQuent',
      version='1.7',
      description='Eloqua automation utility bundle',
      author='Mateusz Dąbrowski',
      url='https://github.com/MateuszDabrowski/',
      options=dict(build_exe=buildOptions),
      executables=executables)
