from typing import Optional, TYPE_CHECKING

from django.db import models
from django.db.models.query import QuerySet

from common.constants import (ChatType, MessageDirection, MessageContentType, MessageStatus)
if TYPE_CHECKING:
    from bot.models import (BotUser, Chat, Message)


class BotManager(models.Manager):
    """Класс менеджеров модели bot.

    Содержит методы для автоматизированного соотнесения идентификаторов ботов
    и обработчиков соответствующих социальных платформ."""

    def get_bot_id_by_type(self, bot_type: int) -> int:
        return self.get(bot_type=bot_type).id

    def get_bot_type_by_id(self, bot_id: int) -> int:
        return self.get(bot_id=bot_id).bot_type


class BotUserManager(models.Manager):
    def get_or_create_user(self, bot_id: int, messenger_user_id: Optional[str], user_name: Optional[str]) -> 'BotUser':
        user, created = self.get_or_create(bot_id=bot_id, messenger_user_id=messenger_user_id)
        if created:
            user.name = user_name
            user.save()
        return user


class ChatManager(models.Manager):
    def get_or_create_chat(self,
                           bot_id: int,
                           chat_id_in_messenger: str,
                           chat_type: ChatType,
                           user: 'BotUser') -> 'Chat':

        chat, created = self.get_or_create(
            bot_id=bot_id,
            id_in_messenger=chat_id_in_messenger,
            type=chat_type.value,
            bot_user=user
        )
        return chat


class MessageManager(models.Manager):
    """Класс для управления моделью Message."""

    def save_message(self,
                     bot_id: int,
                     chat_id_in_messenger: str,
                     chat_type: ChatType,
                     message_direction: MessageDirection,
                     message_content_type: MessageContentType,
                     messenger_user_id: Optional[str],
                     user_name: Optional[str],
                     message_text: Optional[str] = '',
                     message_id_in_messenger: Optional[str] = '') -> 'Message':
        """Сохраняет входящие/исходящие сообщения, обновляет соответствующие поля активности чатов."""

        from .models import BotUser, Chat
        # can't import the models at the top of the file because of a circular dependency
        user = BotUser.objects.get_or_create_user(bot_id, messenger_user_id, user_name)
        chat = Chat.objects.get_or_create_chat(bot_id, chat_id_in_messenger, chat_type, user)
        message = self.create(
            bot_id=bot_id,
            bot_user=user,
            chat=chat,
            direction=message_direction.value,
            content_type=message_content_type.value,
            id_in_messenger=message_id_in_messenger,
            text=message_text,
        )
        if message_direction == MessageDirection.RECEIVED:
            message.status = MessageStatus.DELIVERED.value
        message.save()
        # save message in chat last message
        chat.last_message_time = message.created_at
        chat.last_message_text = message.text
        chat.save()

        return message

    def set_sent(self, message_id: int) -> None:
        """Устанавливает статус SENT сообщениям, успешно отправленным через API платформы."""

        message = self.get(id=message_id)
        message.status = MessageStatus.SENT.value
        message.save()

    def get_chat_messages(self, chat_id: int) -> 'QuerySet[Message]':
        return self.filter(chat_id=chat_id).order_by('created_at').all()
