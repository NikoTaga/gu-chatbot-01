"""Модуль исключений, связанных с работой клиентов социальных платформ."""


class OkServerError(Exception):
    """Возникает при возврате invocation-error в заголовках ответа от ОК."""

    def __init__(self, code: str, text: str) -> None:
        super().__init__(
            f'OK error: code {code} -> {text}"'
        )


class JivoServerError(Exception):
    """Возникает при возврате ключа error в теле ответа json от Jivo."""

    def __init__(self, code: str, text: str) -> None:
        super().__init__(
            f'JIVO error: code {code} -> {text}"'
        )
