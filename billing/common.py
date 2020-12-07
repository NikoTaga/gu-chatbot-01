from typing import Dict, Any

from billing.constants import PaymentSystems
from billing.paypal.client import PaypalClient, PaymentSystemClient
from billing.stripe.client import StripeClient


class PaymentClientFactory:
    """Создаёт инстанс клиента социальной платформы по типу платформы."""

    types: Dict[int, Any] = {
        PaymentSystems.PAYPAL.value: PaypalClient,
        PaymentSystems.STRIPE.value: StripeClient,
    }

    @classmethod
    def create(cls, bot_type: int) -> PaymentSystemClient:
        return cls.types[bot_type]()
