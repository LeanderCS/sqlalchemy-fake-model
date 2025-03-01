class InvalidAmountError(Exception):
    """Exception raised for invalid amount input."""

    def __init__(self, amount) -> None:

        super().__init__(
            f'Invalid amount "{amount}". Amount must be an integer.'
        )
