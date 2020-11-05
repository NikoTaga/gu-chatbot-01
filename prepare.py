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


VENV_DIR_NAME = "venv"
REQ_FILE = "requirements.txt"
REPO = "https://github.com/manchenkoff/gu-chatbot-01"
# PREPARE_VENV_SCRIPT = 'prepare_venv.py'


# todo think about possible errors and rollback?
def setup_env():
    if platform.system() == "Windows":
        pip = "pip"
        activate_this_file = f"{VENV_DIR_NAME}/Scripts/activate_this.py"
    elif platform.system() in ["Linux", "Darwin"]:
        pip = "pip3"
        activate_this_file = f"{VENV_DIR_NAME}/bin/activate_this.py"
    else:
        print("Unknown OS!\nExiting")
        sys.exit(1)
    # install virtualenv via pip
    subprocess.run([pip, "install", "virtualenv"], check=True)
    # delete existing venv
    if os.path.isdir(VENV_DIR_NAME):
        print("Cleaning existing venv...")
        shutil.rmtree(VENV_DIR_NAME)
    # create new virtualenv
    subprocess.run(["virtualenv", VENV_DIR_NAME], check=True)
    if os.path.isfile(activate_this_file):
        # switch the running script into venv
        exec(
            compile(open(activate_this_file, "rb").read(), activate_this_file, "exec"),
            dict(__file__=activate_this_file),
        )
        # install project requirements
        subprocess.run([pip, "install", "-r", REQ_FILE], check=True)
    # venv_python_file = f'{VENV_DIR_NAME}\\Scripts\\python'
    # if os.path.isfile(venv_python_file):
    #     subprocess.Popen([venv_python_file, PREPARE_VENV_SCRIPT, REQ_FILE])


# check python version
major, minor, patch = platform.python_version_tuple()
if (int(major) == 3 and int(minor) >= 7) or int(major) > 3:
    print("Python version check - OK")
else:
    print(
        "You need to upgrade your Python interpreter to version 3.7 at least!\nExiting..."
    )
    sys.exit(1)

# if there is a parameter passed - interpret it as a project directory name, else use '.'
if len(sys.argv) > 1:
    WORKING_DIRECTORY = sys.argv[1]
else:
    WORKING_DIRECTORY = "."

print(f"working in {WORKING_DIRECTORY}")

if not os.path.isdir(WORKING_DIRECTORY):
    os.mkdir(WORKING_DIRECTORY)
# if working_directory is empty - git clone the repo into it
if not os.listdir(WORKING_DIRECTORY):
    subprocess.run(["git", "clone", REPO, WORKING_DIRECTORY], check=True)

# chdir into the working_directory and proceed to set up the virtualenv
os.chdir(WORKING_DIRECTORY)
setup_env()
