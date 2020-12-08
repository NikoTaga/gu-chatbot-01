from django.contrib import admin

from .models import (Bot, BotUser, Chat, Message)


@admin.register(Bot)
class BotAdmin(admin.ModelAdmin):
    """Класс с настройками для работы с моделью Bot в админке Django."""

    readonly_fields = ('created_at', 'updated_at')
    list_display = ('name', 'bot_type')
    list_filter = ('bot_type',)


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    """Класс с настройками для работы с моделью Chat в админке Django."""

    readonly_fields = ('created_at', 'updated_at')
    list_display = ('id',
                    'bot',
                    'name',
                    'id_in_messenger',
                    'bot_user',
                    'created_at',
                    'last_message_time',
                    'last_message_text')
    list_filter = ('bot',)
    search_fields = ('id__exact', 'bot_user_id__exact', 'bot_user_id__messenger_user_id__exact')


@admin.register(BotUser)
class BotUserAdmin(admin.ModelAdmin):
    """Класс с настройками для работы с моделью BotUser в админке Django."""

    readonly_fields = ('created_at', 'updated_at')
    list_display = ('bot', 'name', 'messenger_user_id', 'created_at', 'updated_at')
    list_filter = ('bot',)
    search_fields = ('id__exact', 'messenger_user_id__exact', 'name')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Класс с настройками для работы с моделью Message в админке Django."""

    readonly_fields = (
        'created_at',
        'updated_at',
    )
    list_display = (
        'bot',
        'chat',
        'bot_user',
        'short_text',
        'content_type',
        'created_at',
        'direction',
        'status',
    )
    list_filter = ('bot', 'content_type', 'direction')
    search_fields = (
        'id__exact',
        'chat_id__exact',
        'bot_user_id__exact',
    )
