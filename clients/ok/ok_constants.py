import os
from enum import Enum


OK_TOKEN = os.getenv('OK_TOKEN')


class OkButtonType(Enum):
    CALLBACK = 'CALLBACK'
    LINK = 'LINK'
    REQUEST_CONTACT = 'REQUEST_CONTACT'
    REQUEST_GEO_LOCATION = 'REQUEST_GEO_LOCATION'


class OkButtonIntent(Enum):
    DEFAULT = 'DEFAULT'
    POSITIVE = 'POSITIVE'
    NEGATIVE = 'NEGATIVE'


# unused
class OkPayloadCallType(Enum):
    AUDIO = 'AUDIO'
    VIDEO = 'VIDEO'


# unused
class OkPayloadCallHangupType(Enum):
    CANCELED = 'CANCELED'
    REJECTED = 'REJECTED'
    HUNGUP = 'HUNGUP'
    MISSED = 'MISSED'


class OkAttachmentType(Enum):
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


# unused
class OkPrivacyWarningType(Enum):
    SCREENSHOT = 'SCREENSHOT'
    SCREENCAST = 'SCREENCAST'


class OkWebhookType(Enum):
    MESSAGE_CREATED = 'MESSAGE_CREATED'
    MESSAGE_CALLBACK = 'MESSAGE_CALLBACK'
    CHAT_SYSTEM = 'CHAT_SYSTEM'


class OkSystemWebhookType(Enum):
    CHAT_STARTED = 'CHAT_STARTED'
