import logging
from uuid import UUID

from django.core.exceptions import ObjectDoesNotExist

from .enums import Currency, TransactionStatus
from .exceptions import (
    TransactionCreationError,
    TransactionFailedError,
    TransactionRelatedEntityNotFoundError,
)
from .factory import Transaction as TransactionABC
from .factory import TransactionFactory
from .models import Balance, Customer, Payable, Transaction


class TransactionService:
    def process(self, data: dict) -> dict[str, str]:
        """
        Process a transaction and applies specific rules.
        Returns transaction_id and status.
        If the transaction fails, client receives a failed status response.
        """
        try:
            customer: Customer = self._get_customer_with_balance(data["customer_id"])
            transaction: Transaction = self._create_pending_transaction(data)
            logging.info(f"[payments.service] pending transaction created for {customer.id}")

            factory: TransactionABC = TransactionFactory.create(transaction.method)
            payable: Payable = factory.create_payable(transaction, customer)

            factory.apply_payable_on_balance(payable, customer)
            factory.finish_transaction(transaction)
        except TransactionRelatedEntityNotFoundError as err:
            raise TransactionRelatedEntityNotFoundError(
                f"Not Found: {err}"
            ) from err
        except TransactionCreationError as err:
            raise TransactionFailedError(
                f"Transaction creation failed: {err}"
            ) from err
        except Exception as err:
            factory.fail_transaction(transaction)
            raise TransactionFailedError(
                f"Transaction processing failed: {err}"
            ) from err

        return {"customer_id": data["customer_id"], "status": transaction.status}

    def _create_pending_transaction(self, data: dict) -> Transaction:
        try:
            default_expected_fee = 0.0
            return Transaction.objects.create(
                value=data["value"],
                currency=data.get("currency", Currency.BRL),
                description=data["description"],
                method=data["method"],
                status=TransactionStatus.PENDING,
                expected_fee=default_expected_fee,
                card_number=data["card_number"],
                card_owner=data["card_owner"],
                card_expiration_year=data["card_expiration_year"],
                card_verification_code=data["card_verification_code"],
            )
        except Exception as err:
            raise TransactionCreationError(
                f"[payments.service] Failed to create pending transaction: {err}"
            ) from err

    def _get_customer_with_balance(self, customer_id: UUID) -> Customer:
        try:
            customer = Customer.objects.get(id=customer_id)
        except ObjectDoesNotExist as err:
            raise TransactionRelatedEntityNotFoundError(
                f"Customer {customer_id} not found."
            ) from err

        balance = Balance.objects.filter(customer=customer).first()
        if not balance:
            raise TransactionRelatedEntityNotFoundError(
                f"Balance not found for customer {customer_id}."
            )

        customer.balance = balance

        return customer
