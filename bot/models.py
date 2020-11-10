from django.db import models

from constants import (BotType, ChatType, MessageContentType, MessageDirection, MessageStatus)
from ecom_chatbot.settings import LANGUAGES


class TrackableUpdateCreateModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        abstract = True


class Bot(TrackableUpdateCreateModel):
    name = models.CharField('Name', max_length=255, blank=True)
    bot_type = models.PositiveSmallIntegerField('Bot Type', choices=BotType.choices())

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = 'Bot'
        verbose_name_plural = 'Bots'
        app_label = 'bot'
        ordering = ['bot_type']


class BotUser(TrackableUpdateCreateModel):
    bot = models.ForeignKey(Bot, verbose_name='Bot', on_delete=models.CASCADE, db_index=True)

    messenger_user_id = models.CharField('MessengerUserId', max_length=64)
    messenger_user_url = models.URLField('MessengerUserURL', max_length=2047, null=True, blank=True)

    name = models.CharField('Name', max_length=255, null=True, blank=True)
    avatar_url = models.URLField('Avatar', max_length=2047, null=True, blank=True)

    lang_code = models.CharField('User language', choices=LANGUAGES, max_length=2)

    def __str__(self) -> str:
        return f'#{self.id} <{self.bot}> {self.name}'

    class Meta:
        verbose_name = 'Bot user'
        verbose_name_plural = 'BotUsers'
        app_label = 'bot'
        ordering = ['bot', '-created_at']
        unique_together = (("bot", "messenger_user_id"),)


class Chat(TrackableUpdateCreateModel):
    bot = models.ForeignKey(Bot, verbose_name='Bot', on_delete=models.CASCADE, db_index=True)
    type = models.PositiveSmallIntegerField('Type', choices=ChatType.choices())
    bot_user = models.OneToOneField(
        BotUser,
        verbose_name='BotUser',
        on_delete=models.CASCADE,
        db_index=True,
        blank=True,
        null=True,
    )

    id_in_messenger = models.CharField('Id in messenger', max_length=64)
    url_in_messenger = models.URLField('URLInMessenger', max_length=2047, null=True, blank=True)
    name = models.CharField('Name', max_length=255, null=True, blank=True)
    avatar_url = models.URLField('Avatar', max_length=2047, null=True, blank=True)

    last_message_time = models.DateTimeField(blank=True, null=True)
    last_message_text = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self) -> str:
        return f'#{self.id} <{self.bot}> {self.id_in_messenger}'

    class Meta:
        verbose_name = 'Chat'
        verbose_name_plural = 'Chats'
        app_label = 'bot'
        ordering = ('-last_message_time', 'bot',)
        unique_together = (('bot', 'id_in_messenger'),)
        index_together = (
            ('bot', 'id_in_messenger'),
        )


class Message(TrackableUpdateCreateModel):
    bot = models.ForeignKey(Bot, verbose_name='Bot', on_delete=models.CASCADE, db_index=True)
    bot_user = models.ForeignKey(BotUser, verbose_name='Bot user', on_delete=models.SET_NULL, blank=True, null=True)
    chat = models.ForeignKey(
        Chat,
        verbose_name='Chat',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        db_index=True,
    )
    status = models.PositiveSmallIntegerField(
        'Status',
        choices=MessageStatus.choices(),
        default=MessageStatus.NEW.value,
    )
    direction = models.PositiveSmallIntegerField('Direction', choices=MessageDirection.choices())
    content_type = models.PositiveSmallIntegerField('Content type', choices=MessageContentType.choices())

    id_in_messenger = models.CharField('ID in messenger', max_length=64, db_index=True, blank=True, null=True)
    reply_id_in_messenger = models.CharField(
        'Reply ID in messenger',
        max_length=64,
        null=True,
        blank=True,
        db_index=True,
    )
    ts_in_messenger = models.DateTimeField('Timestamp in messenger', blank=True, null=True)

    text = models.TextField('Text', null=True, blank=True)
    image_url = models.URLField('Image', max_length=2047, blank=True, null=True)
    file_url = models.URLField('File', max_length=2047, blank=True, null=True)
    video_url = models.URLField('Video', max_length=2047, blank=True, null=True)

    language = models.CharField('Language code', max_length=11, default='ru')

    @property
    def short_text(self) -> str:
        return f'{self.text[:50]}...' if self.text and len(self.text) > 50 else self.text

    def __str__(self) -> str:
        return f'<{self.bot}> {self.content_type} {self.direction}'

    class Meta:
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
        app_label = 'bot'
        ordering = ['-created_at', 'bot', 'bot_user']
