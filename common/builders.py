import logging
from typing import List, Dict, Any, Optional

from clients.ok.ok_constants import OkButtonIntent, OkButtonType, OkAttachmentType
from clients.ok.ok_entities import (OkOutgoingMessage, OkMessage, OkRecipient, OkButton, OkAttachment, OkPayload,
                                    OkButtons)
from common.constants import MessageDirection, MessageContentType, GenericTemplateActionType
from common.entities import Payload, EventCommandToSend, InlineButton, GenericTemplateAction, Callback


logger = logging.getLogger('root')


class ECTSBuilder:
    _command: EventCommandToSend

    def get_command(self) -> EventCommandToSend:
        return self._command

    def form_preset(self, bot_id: int, chat_id_in_messenger: str) -> None:
        pl = Payload()
        pl.direction = MessageDirection.SENT
        pl.text = None
        cmd = EventCommandToSend(bot_id, chat_id_in_messenger, MessageContentType.TEXT, pl)

        self._command = cmd

    def add_text(self, text: str) -> None:
        cmd = self._command
        cmd.content_type = MessageContentType.TEXT
        cmd.payload.text = text

    def _build_buttons(self, button_data: List[Dict[str, Any]]) -> List[InlineButton]:
        buttons = []
        for entry in button_data:
            action = GenericTemplateAction(GenericTemplateActionType.POSTBACK)
            action.payload = Callback.Schema().dumps({
                 'type': entry['type'],
                 'id': entry['id'],
            })
            btn = InlineButton(entry['title'], action)
            buttons.append(btn)

        logger.debug(f'Builder: {buttons}')
        return buttons

    def add_buttons(self, button_data: List[Dict[str, str]]) -> None:
        cmd = self._command
        cmd.content_type = MessageContentType.INLINE
        cmd.inline_buttons = self._build_buttons(button_data)


class OkOutgoingBuilder:
    _command: OkOutgoingMessage

    def get_command(self) -> OkOutgoingMessage:
        return self._command

    def form_preset(self, chat_id_in_messenger: str, text: Optional[str]) -> None:
        recipient = OkRecipient(chat_id_in_messenger)
        message = OkMessage(text=text)
        self._command = OkOutgoingMessage(recipient, message)

    def _build_buttons(self, button_data: List[Dict[str, Optional[str]]]) -> List[List[OkButton]]:
        buttons = []
        for entry in button_data:
            ok_btn = OkButton(OkButtonType.CALLBACK, entry['text'], OkButtonIntent.POSITIVE)
            ok_btn.payload = entry['payload']
            buttons.append([ok_btn])

        return buttons

    def add_buttons(self, button_data: List[Dict[str, Optional[str]]]) -> None:
        buttons = OkButtons(self._build_buttons(button_data))
        pl = OkPayload(
            keyboard=buttons,
        )
        attachment = OkAttachment(OkAttachmentType.INLINE_KEYBOARD, pl)
        self._command.message.attachment = attachment


class MessageDirector:
    def __init__(self) -> None:
        self._builder: Any = None

    def create_ects(
            self,
            bot_id: int,
            chat_id_in_messenger: str,
            text: str,
            button_data: Optional[List[Dict[str, Any]]] = None
    ) -> EventCommandToSend:

        self._builder = ECTSBuilder()

        self._builder.form_preset(bot_id, chat_id_in_messenger)
        self._builder.add_text(text)
        if button_data is not None:
            self._builder.add_buttons(button_data)

        return self._builder.get_command()

    def create_ok_message(self, ects: EventCommandToSend) -> OkOutgoingMessage:

        self._builder = OkOutgoingBuilder()

        self._builder.form_preset(ects.chat_id_in_messenger, ects.payload.text)
        # self._builder.add_text(text)
        if ects.inline_buttons:
            button_data = [{
                'text': entry.text,
                'payload': entry.action.payload,
            } for entry in ects.inline_buttons]
            assert button_data is not None
            self._builder.add_buttons(button_data)

        return self._builder.get_command()
