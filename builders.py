from abc import ABC
from typing import List, Dict, Union, Any

from constants import MessageDirection, MessageContentType, CallbackType, GenericTemplateActionType
from entities import Payload, EventCommandToSend, InlineButton, GenericTemplateAction, Callback


class ECTSBuilder:
    def __init__(self) -> None:
        self._command: EventCommandToSend

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

        print(buttons)
        return buttons

    def add_buttons(self, button_data: List[Dict[str, str]]) -> None:
        cmd = self._command
        cmd.content_type = MessageContentType.INLINE
        cmd.inline_buttons = self._build_buttons(button_data)


class ECTSDirector:
    def __init__(self) -> None:
        self._builder = ECTSBuilder()

    # @property
    # def builder(self):
    #     return self._builder
    #
    # @builder.setter
    # def builder(self, builder: ECTSBuilder):
    #     self._builder = builder

    def create_message(
            self,
            bot_id: int = None,
            chat_id_in_messenger: str = None,
            text: str = None,
            button_data: List[Dict[str, Any]] = None
    ) -> EventCommandToSend:

        self._builder.form_preset(bot_id, chat_id_in_messenger)
        self._builder.add_text(text)
        if button_data:
            self._builder.add_buttons(button_data)

        return self._builder.get_command()


# class AbstractECRBuilder(ABC):
#
#
#
#
# class ECRBuilder