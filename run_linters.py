import subprocess
import platform
import os
import glob
import sys

PATH = os.getcwd()
DIR_REPORTS = 'report_linters'

if platform.system() == 'Windows':
    PATH_LINT = f'{PATH}\{DIR_REPORTS}'
elif platform.system() in ['Linux', 'Darwin']:
    PATH_LINT = f'{PATH}/{DIR_REPORTS}'
else:
    print('Unknown OS!\nExiting')
    sys.exit(1)

access_rights = 0o777
mode_type = str(input('Для интерактивного режима введите Y , для записи отчёта в файл введите любой символ:\n')).upper()

if not os.path.exists(PATH_LINT):
    os.mkdir(PATH_LINT, access_rights)

files_in_directory = glob.glob(os.path.join(PATH_LINT, '*.*'))
for file in files_in_directory:
    os.remove(file)

if mode_type == 'Y':
    subprocess.run(['mypy',	'./billing', './bot', './clients', './ecom_chatbot', './shop', './'])
    subprocess.run(['flake8', './'])
else:
    subprocess.run(['mypy', './billing', './bot', './clients', './ecom_chatbot', './shop', './'])
    subprocess.run(['flake8', '--output-file=report_linters/flake8.log', './'])
