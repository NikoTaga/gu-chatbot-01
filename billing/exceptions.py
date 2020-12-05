class UpdateCompletedCheckoutError(Exception):
    def __init__(self, pk, system, tracking_id, new_status):
        super().__init__(
            f'Trying to update a completed checkout #{pk} from:{system}, id: {tracking_id}\n'
            f' with status {new_status}'
        )