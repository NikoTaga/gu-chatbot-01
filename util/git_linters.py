import subprocess
import platform
import os
import glob
import sys

PATH = os.getcwd()
DIR_REPORTS = '../report_linters'
DIRS = ['./billing', './bot', './clients', './ecom_chatbot', './shop', './']
# формирует список папок и файлов для проверки #
# DIRS = os.listdir(PATH)

if platform.system() == 'Windows':
    PATH_LINT = r'%s\%s' % (PATH, DIR_REPORTS)
elif platform.system() in ['Linux', 'Darwin']:
    PATH_LINT = r'%s/%s' % (PATH, DIR_REPORTS)
else:
    print('Unknown OS!\nExiting')
    sys.exit(1)

access_rights = 0o777

if not os.path.exists(PATH_LINT):
    os.mkdir(PATH_LINT, access_rights)


files_in_directory = glob.glob(os.path.join(PATH_LINT, '*.*'))
for file in files_in_directory:
    os.remove(file)


for directory in DIRS:
    subprocess.run(['mypy', directory])
subprocess.run(['flake8', './'])
