from cx_Freeze import setup, Executable

buildOptions = dict(include_files=['README.md', 'LICENSE', 'utils', 'utils.json'],
                    packages=['pyperclip', 'csv', 're', 'os', 'sys', 'pickle', 'requests', 'idna',
                              'platform', 'encodings', 'colorama', 'json', 'multiprocessing',
                              'time', 'datetime', 'getpass', 'base64', 'webbrowser'])

base = 'Console'

executables = [
    Executable('elquent.py', base=base)
]

setup(name='ELQuent',
      version='1.4',
      description='Eloqua automation utility bundle',
      author='Mateusz Dąbrowski',
      url='https://github.com/MateuszDabrowski/',
      options=dict(build_exe=buildOptions),
      executables=executables)
