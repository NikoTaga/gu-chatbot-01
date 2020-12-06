"""Модуль исключений, связанных с работой платёжных систем."""


class UpdateCompletedCheckoutError(Exception):
    """Возникает при попытке обновить Checkout, уже имеющий статус COMPLETE."""

    def __init__(self, pk: int, system: str, tracking_id: str, new_status: str) -> None:
        super().__init__(
            f'Trying to update a completed checkout #{pk} from: {system}, id: {tracking_id}\n'
            f' with status "{new_status}"'
        )
