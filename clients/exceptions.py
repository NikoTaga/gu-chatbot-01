"""Модуль исключений, связанных с работой клиентов социальных платформ."""


class OkServerError(Exception):
    """Возникает при возврате invocation-error в заголовках ответ от ОК."""

    def __init__(self, code: int, text: str) -> None:
        super().__init__(
            f'OK error: code {code} -> {text}"'
        )
