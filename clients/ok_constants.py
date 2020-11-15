from enum import Enum


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
class PayloadCallType(Enum):
    AUDIO = 'AUDIO'
    VIDEO = 'VIDEO'


# unused
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


# unused
class PrivacyWarningType(Enum):
    SCREENSHOT = 'SCREENSHOT'
    SCREENCAST = 'SCREENCAST'


class OkWebhookType(Enum):
    MESSAGE_CREATED = 'MESSAGE_CREATED'
    MESSAGE_CALLBACK = 'MESSAGE_CALLBACK'
    CHAT_SYSTEM = 'CHAT_SYSTEM'


class OkSystemWebhookType(Enum):
    CHAT_STARTED = 'CHAT_STARTED'
