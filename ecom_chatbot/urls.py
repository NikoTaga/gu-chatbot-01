from django.contrib import admin
from django.urls import path, include

from shop.views import index_page
from bot.views import jivo_webhook, ok_webhook, chat_view


urlpatterns = [
    path('', index_page),
    path('admin/', admin.site.urls),
    path('ok_webhook/', ok_webhook),
    path('jivo_webhook/test', jivo_webhook),
    path('chats/<int:pk>/', chat_view),
    path('chats/', chat_view),
    path('billing/', include('billing.urls', namespace='billing')),
]
