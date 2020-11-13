from enum import Enum


class ButtonType(Enum):
    CALLBACK = 'CALLBACK'
    LINK = 'LINK'
    REQUEST_CONTACT = 'REQUEST_CONTACT'
    REQUEST_GEO_LOCATION = 'REQUEST_GEO_LOCATION'


class ButtonIntent(Enum):
    DEFAULT = 'DEFAULT'
    POSITIVE = 'POSITIVE'
    NEGATIVE = 'NEGATIVE'


class PayloadCallType(Enum):
    AUDIO = 'AUDIO'
    VIDEO = 'VIDEO'


class PayloadCallHangupType(Enum):
    CANCELED = 'CANCELED'
    REJECTED = 'REJECTED'
    HUNGUP = 'HUNGUP'
    MISSED = 'MISSED'


class AttachmentType(Enum):
    IMAGE = 'IMAGE'
    VIDEO = 'VIDEO'
    AUDIO = 'AUDIO'
    SHARE = 'SHARE'
    FILE = 'FILE'
    CONTACT = 'CONTACT'
    INLINE_KEYBOARD = 'INLINE_KEYBOARD'
    LOCATION = 'LOCATION'
    MUSIC = 'MUSIC'
    CALL = 'CALL'
    PRESENT = 'PRESENT'
    STICKER = 'STICKER'


class PrivacyWarningType(Enum):
    SCREENSHOT = 'SCREENSHOT'
    SCREENCAST = 'SCREENCAST'


class WebhookType(Enum):
    MESSAGE_CREATED = 'MESSAGE_CREATED'
    MESSAGE_CALLBACK = 'MESSAGE_CALLBACK'
    CHAT_SYSTEM = 'CHAT_SYSTEM'


class SystemWebhookType(Enum):
    CHAT_STARTED = 'CHAT_STARTED'
