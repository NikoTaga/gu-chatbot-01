import subprocess
import sys

DIRS = ['./billing', './bot', './clients', './ecom_chatbot', './shop']
# IGNORE_FLAKE = '--extend-ignore=D210'


for directory in DIRS:
    result = subprocess.run(['mypy', directory])
    result_code = result.returncode
    if result_code == 0:
        print('Mypy: ошибки оформления кода не найдены.')
    else:
        print('Mypy: найдены ошибки оформления кода!!!')
        sys.exit(1)


result = subprocess.run(['flake8', './'])
result_code = result.returncode
if result_code == 0:
    print('flake8: ошибки оформления кода не найдены.')
else:
    print('flake8: найдены ошибки оформления кода!!!')
    sys.exit(1)
