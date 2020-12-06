"""Модуль с набором констант и перечислений относящихся к интеграции с платёжными системами."""

from enum import Enum
from constants import Choice


STRIPE_PUBLIC_KEY = 'pk_test_51HqMI4J7UqTQQfE9i7b78Qa91U3AHOne4nzq6beJbw2WCXhdM3jtycetMAzJMZOTTKGnjs0M1tfSDkoG0UKx' \
                    '4gHt00AT3RCDwP'
STRIPE_SECRET_KEY = 'sk_test_51HqMI4J7UqTQQfE9r7ZnxzdoDR4PpqoZCbekqg1TOIlTQZTevahpbO0YAMVoH02VKtRfXBdGn5ltwh9jCptn' \
                    'I8B100eoXJM7nE'
STRIPE_WHSEC_KEY = 'whsec_wtG2TSXjPejSZ9Z1OXkhhCCFUKXNmKVp'


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


class StripeMode(Enum):
    PAYMENT = 'payment'
    SETUP = 'setup'
    SUBSCRIPTION = 'subscription'


class StripePaymentMethod(Enum):
    CARD = 'card'


class StripeCurrency(Enum):
    RUB = 'rub'
    USD = 'usd'


class Currency(Enum):
    RUB = 'RUB'
    USD = 'USD'


class PaypalGoodsCategory(Enum):
    PHYSICAL_GOODS = 'PHYSICAL_GOODS'
    DIGITAL_GOODS = 'DIGITAL_GOODS'
