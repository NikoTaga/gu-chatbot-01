"""Модуль с набором констант и перечислений относящихся к интеграции с платёжными системами."""

import os
from enum import Enum

SITE_HTTPS_URL = os.getenv("SITE_HTTPS_URL")

PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID")
PAYPAL_CLIENT_SECRET = os.getenv("PAYPAL_CLIENT_SECRET")
PAYPAL_WEBHOOK_ID = os.getenv("PAYPAL_WEBHOOK_ID")

STRIPE_PUBLIC_KEY = os.getenv("STRIPE_PUBLIC_KEY")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WHSEC_KEY = os.getenv("STRIPE_WHSEC_KEY")


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
