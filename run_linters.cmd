mypy --config-file mypy.ini --lineprecision-report report_linters ./billing ./bot ./clients ./ecom_chatbot ./shop
pause
flake8 --config=.flake8 --output-file=report_linters/flake8.log ./
pause