"""
ASGI config for ecom_chatbot project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/asgi/
"""

import os
from pathlib import Path
from dotenv import load_dotenv

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecom_chatbot.settings')
project_folder = Path(__file__).parent.parent.absolute()
load_dotenv(project_folder.joinpath('.env'))

application = get_asgi_application()
