from typing import Dict, Any, TYPE_CHECKING
from abc import ABC, abstractmethod

if TYPE_CHECKING:
    from django.http import HttpRequest


class PaymentSystemClient(ABC):
    """Абстрактный интерфейс, описывающий поведение платёжной системы."""

    @abstractmethod
    def check_out(self, order_id: int, product_id: int) -> str:
        pass

    @staticmethod
    @abstractmethod
    def verify(request: 'HttpRequest') -> bool:
        pass

    @abstractmethod
    def capture(self, wh_data: Dict[str, Any]) -> None:
        pass

    @staticmethod
    @abstractmethod
    def fulfill(data: Dict[str, Any]) -> None:
        pass
