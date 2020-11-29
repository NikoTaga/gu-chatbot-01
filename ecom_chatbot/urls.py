"""ecom_chatbot URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from shop.views import index_page
from billing.views import paypal_webhook, stripe_webhook, stripe_redirect
from bot.views import jivosite_webhook, ok_test_webhook, ok_webhook, chat_list, chat_view, jivo_test_webhook


urlpatterns = [
    path('', index_page),
    path('admin/', admin.site.urls),
    path('ok_webhook/', ok_webhook),
    path('ok_test/', ok_test_webhook),
    path('pp_webhook/', paypal_webhook),
    path('stripe_webhook/', stripe_webhook),
    path('stripe_redirect/<str:cid>', stripe_redirect),
    path('jivo_webhook/test', jivo_test_webhook),
    path('jivosite_webhook/', jivosite_webhook),
    path('chat/<int:pk>/', chat_view),
    path('chats/', chat_list),
]
