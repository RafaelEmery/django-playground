from uuid import uuid4

from .serializers import TransactionProcessRequestSerializer


class TransactionService:
    def process(self, data: TransactionProcessRequestSerializer) -> dict[str, str]:
        """
        Process a transaction and applies specific rules.
        Returns transaction_id and status.
        If the transaction fails, client receives a failed status response.
        """
        return {"id": str(uuid4()), "status": "failed"}
