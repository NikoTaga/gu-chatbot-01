"""
WSGI config for ecom_chatbot project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/wsgi/
"""

import os
from pathlib import Path
from dotenv import load_dotenv

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecom_chatbot.settings')
project_folder = Path(__file__).parent.parent.absolute()
load_dotenv(project_folder.parent.joinpath('.env'))

application = get_wsgi_application()
