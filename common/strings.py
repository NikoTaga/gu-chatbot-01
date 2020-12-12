import configparser
import logging
from enum import Enum


logger = logging.getLogger('root')


config = configparser.ConfigParser()
config.read('common/strings.ini')
logger.debug(config.sections())


class PayPalStrings(Enum):
    LINK_PATTERN = config['billing']['PayPalCheckoutLink']
    WEBHOOK_APPROVED = config['billing']['PayPalOrderApproved']
    WEBHOOK_COMPLETED = config['billing']['PayPalCaptureCompleted']


class StripeStrings(Enum):
    SESSION_COMPLETED = config['billing']['StripeSessionCompleted']
    LINK_PATTERN = config['billing']['StripeCheckoutLink']
    LINK_SUCCESS = config['billing']['StripeRedirectSuccess']
    LINK_CANCEL = config['billing']['StripeRedirectCancel']


class DialogButtons(Enum):
    START_SESSION = config['dialog']['StartSessionButton']
    ORDER_PRODUCT = config['dialog']['OrderProductButton']
    PAYPAL_OPTION = config['dialog']['PayPalOptionButton']
    STRIPE_OPTION = config['dialog']['StripeOptionButton']


class DialogPhrases(Enum):
    SESSION_GREETING = config['dialog']['SessionGreeting']
    CHOOSE_CATEGORY = config['dialog']['ChooseCategory']
    CHOOSE_PRODUCT = config['dialog']['ChooseProduct']
    ORDER_PRODUCT = config['dialog']['OrderProduct']
    ORDER_CONFIRM = config['dialog']['OrderConfirm']
    PAYMENT_LINK = config['dialog']['PaymentLink']


class NotifyPhrases(Enum):
    PAYMENT_SUCCESS = config['notify']['PaymentSuccess']


class JivoStrings(Enum):
    API_LINK = config['clients']['JivoAPILink']
    INVITE_OPERATOR = config['clients']['JivoInviteOperator']


class OkStrings(Enum):
    IP_POOL = config['clients']['OkIpPool']
    API_LINK = config['clients']['OkAPILink']
