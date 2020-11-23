from enum import Enum
from constants import Choice


class PaymentSystems(Choice):
    PAYPAL = 0
    STRIPE = 1
    CLICK = 2
    PAYMO = 3


class PaypalOrderStatus(Enum):
    CREATED = 'CREATED'
    SAVED = 'SAVED'
    APPROVED = 'APPROVED'
    VOIDED = 'VOIDED'
    COMPLETED = 'COMPLETED'
    PAYER_ACTION_REQUIRED = 'PAYER_ACTION_REQUIRED'


class PaypalIntent(Enum):
    CAPTURE = 'CAPTURE'
    AUTHORIZE = 'AUTHORIZE'


class PaypalShippingPreference(Enum):
    GET_FROM_FILE = 'GET_FROM_FILE'
    NO_SHIPPING = 'NO_SHIPPING'
    SET_PROVIDED_ADDRESS = 'SET_PROVIDED_ADDRESS'


class PaypalUserAction(Enum):
    CONTINUE = 'CONTINUE'
    PAY_NOW = 'PAY_NOW'


class Currency(Enum):
    RUB = 'RUB'


class PaypalGoodsCategory(Enum):
    PHYSICAL_GOODS = 'PHYSICAL_GOODS'
    DIGITAL_GOODS = 'DIGITAL_GOODS'
