class TransactionRelatedEntityNotFoundError(Exception):
    """Exception raised for not found resources."""
    pass


class TransactionCreationError(Exception):
    """Exception raised for errors during pending transaction creation."""
    pass


class TransactionFailedError(Exception):
    """Exception raised for failed transactions."""
    pass


class PayableScheduledError(Exception):
    """Exception raised for error on scheduled payables."""
    pass
