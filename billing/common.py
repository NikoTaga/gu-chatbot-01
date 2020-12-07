from abc import ABC, abstractmethod
from typing import Dict, Any

from django.http import HttpRequest

from billing.constants import PaymentSystems
from billing.paypal.client import PaypalClient
from billing.stripe.client import StripeClient


class PaymentSystemClient(ABC):
    """Абстрактный интерфейс, описывающий поведение платёжной системы."""

    @abstractmethod
    def check_out(self, order_id: int, product_id: int) -> str:
        pass

    @staticmethod
    @abstractmethod
    def verify(request: HttpRequest) -> bool:
        pass

    @abstractmethod
    def capture(self, wh_data: Dict[str, Any]) -> None:
        pass

    @staticmethod
    @abstractmethod
    def fulfill(data: Dict[str, Any]) -> None:
        pass


class PaymentClientFactory:
    """Создаёт инстанс клиента социальной платформы по типу платформы."""

    types: Dict[int, Any] = {
        PaymentSystems.PAYPAL.value: PaypalClient,
        PaymentSystems.STRIPE.value: StripeClient,
    }

    @classmethod
    def create(cls, bot_type: int) -> PaymentSystemClient:
        return cls.types[bot_type]()
