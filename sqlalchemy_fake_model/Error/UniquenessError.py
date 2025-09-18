class UniquenessError(Exception):
    """
    Exception raised when unique constraint violations occur after max retries.
    """

    def __init__(self, field_name: str, max_retries: int):
        self.field_name = field_name
        self.max_retries = max_retries
        super().__init__(
            f"Failed to generate unique value for field '{field_name}' "
            f"after {max_retries} retries"
        )
