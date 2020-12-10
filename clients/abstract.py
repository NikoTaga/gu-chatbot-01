from typing import Dict, Any, TYPE_CHECKING
from abc import ABC, abstractmethod

from entities import EventCommandToSend, EventCommandReceived

if TYPE_CHECKING:
    from django.http import HttpRequest


class SocialPlatformClient(ABC):
    """Абстрактный интерфейс, описывающий поведение социальной платформы."""

    @abstractmethod
    def parse_webhook(self, wh_data: Dict[str, Any]) -> EventCommandReceived:
        pass

    @abstractmethod
    def send_message(self, payload: EventCommandToSend) -> None:
        pass

    @staticmethod
    @abstractmethod
    def verify_request(request: 'HttpRequest') -> bool:
        pass
