#!/bin/python3
"""Скрипт для автоматизации скачивания дистрибутивов Python проектов с github
и настройки виртуального окружения для них.

Скрипт работает в двух режимах:
1. При запуске в директории с дистрибутивом без параметров - создаёт виртуальное окружение Python
и устанавливает туда пакеты в соответствии с требованиями проекта.
2. При запуске с параметром <имя директории> - выполняет git clone проекта в эту директорию
(если она пуста или не существует), затем создаёт виртуальное окружение и устанавливает туда пакеты в соответствии
с требованиями проекта."""

import platform
import subprocess
import sys
import os
import shutil


VENV_DIR_NAME = 'venv'
REQ_FILE = 'requirements.txt'
REPO = 'https://github.com/manchenkoff/gu-chatbot-01'
PIP = 'pip3'
if platform.system() == 'Windows':
    PIP_ENV = f'{VENV_DIR_NAME}/Scripts/pip3.exe'
    PYTHON = f'{VENV_DIR_NAME}/Scripts/python.exe'
elif platform.system() in ['Linux', 'Darwin']:
    PYTHON = f'{VENV_DIR_NAME}/bin/python3'
    PIP_ENV = f'{VENV_DIR_NAME}/bin/pip3'
else:
    print('Unknown OS!\nExiting')
    sys.exit(1)


# todo think about possible errors and rollback?
def setup_env() -> None:
    # install virtualenv via pip
    subprocess.run([PIP, 'install', 'virtualenv'], check=True)
    # delete existing venv
    if os.path.isdir(VENV_DIR_NAME):
        print('Cleaning existing venv...')
        shutil.rmtree(VENV_DIR_NAME)
    # create new virtualenv
    subprocess.run(['virtualenv', VENV_DIR_NAME], check=True)
    run_preparations()


def run_preparations() -> None:
    # install project requirements
    subprocess.run([PIP_ENV, 'install', '-r', REQ_FILE], check=True)
    # perform migrations
    subprocess.run([PYTHON, 'manage.py', 'makemigrations'], check=True)
    subprocess.run([PYTHON, 'manage.py', 'migrate'], check=True)


# check python version
major, minor, patch = platform.python_version_tuple()
if (int(major) == 3 and int(minor) >= 7) or int(major) > 3:
    print('Python version check - OK')
else:
    print(
        'You need to upgrade your Python interpreter to version 3.7 at least!\nExiting...'
    )
    sys.exit(1)

# if there is a parameter passed - interpret it as a project directory name, else use '.'
if len(sys.argv) > 1:
    WORKING_DIRECTORY = sys.argv[1]
else:
    WORKING_DIRECTORY = '.'

print(f'working in {WORKING_DIRECTORY}')

if not os.path.isdir(WORKING_DIRECTORY):
    os.mkdir(WORKING_DIRECTORY)
# if working_directory is empty - git clone the repo into it
if not os.listdir(WORKING_DIRECTORY):
    subprocess.run(['git', 'clone', REPO, WORKING_DIRECTORY], check=True)

# chdir into the working_directory and proceed to set up the virtualenv
os.chdir(WORKING_DIRECTORY)
setup_env()
