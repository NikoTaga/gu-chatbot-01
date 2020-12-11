from typing import Dict, Any, TYPE_CHECKING

from billing.paypal.client import PaypalClient
from billing.stripe.client import StripeClient

if TYPE_CHECKING:
    from .abstract import PaymentSystemClient


class PaymentClientFactory:
    """Создаёт инстанс клиента социальной платформы по типу платформы."""

    types: Dict[str, Any] = {
        'paypal': PaypalClient,
        'stripe': StripeClient,
    }

    @classmethod
    def create(cls, bot_type: str) -> 'PaymentSystemClient':
        return cls.types[bot_type]()
