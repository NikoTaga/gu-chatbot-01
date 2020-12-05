from typing import List, Dict

from constants import MessageDirection, MessageContentType, CallbackType, GenericTemplateActionType
from entities import Payload, EventCommandToSend, InlineButton, GenericTemplateAction, Callback


class ECTSBuilder:
    def __init__(self):
        self._command = None
        self.callback_type = None

    def get_command(self):
        return self._command

    def form_preset(self, bot_id, chat_id_in_messenger) -> None:
        pl = Payload()
        pl.direction = MessageDirection.SENT
        pl.text = None
        cmd = EventCommandToSend(bot_id, chat_id_in_messenger, MessageContentType.TEXT, pl)

        self._command = cmd

    def add_text(self, text: str) -> None:
        cmd = self._command
        cmd.content_type = MessageContentType.TEXT
        cmd.payload.text = text

    def _build_buttons(self, button_data: List[Dict[str, str]]) -> List[InlineButton]:
        buttons = []
        for entry in button_data:
            btn = InlineButton()
            btn.text = entry['title']
            action = GenericTemplateAction()
            action.type = GenericTemplateActionType.POSTBACK
            action.payload = Callback.Schema().dumps({
                 'type': self.callback_type,
                 'product': entry['id']
            })
            btn.action = action
            buttons.append(btn)

        return buttons

    def add_buttons(self, button_data: List[Dict[str, str]]) -> None:
        cmd = self._command
        cmd.content_type = MessageContentType.INLINE
        cmd.inline_buttons = self._build_buttons(button_data)


class ECTSDirector:
    def __init__(self):
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
            msg_type=None,
            bot_id=None,
            chat_id_in_messenger=None,
            text=None,
            button_data=None
    ) -> EventCommandToSend:

        self._builder.callback_type = msg_type
        self._builder.form_preset(bot_id, chat_id_in_messenger)
        self._builder.add_text(text)
        if button_data:
            self._builder.add_buttons(button_data)

        return self._builder.get_command()

