import logging
from uuid import UUID

from django.core.exceptions import ObjectDoesNotExist

from .enums import Currency, TransactionStatus
from .exceptions import NotFoundError, TransactionFailedError
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
        except NotFoundError as err:
            raise NotFoundError(f"[payments.service] {err}") from err
        except Exception as err:
            self._update_transaction_to_failed(transaction)
            raise TransactionFailedError(
                f"[payments.service] Transaction processing failed: {err}"
            ) from err

        return {"customer_id": data["customer_id"], "status": transaction.status}

    def _create_pending_transaction(self, data: dict) -> Transaction:
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

    def _update_transaction_to_failed(self, transaction):
        if transaction:
            transaction.status = TransactionStatus.FAILED
            transaction.save()

    def _get_customer_with_balance(self, customer_id: UUID) -> Customer:
        try:
            customer = Customer.objects.get(id=customer_id)
        except ObjectDoesNotExist as err:
            raise NotFoundError(f"Customer {customer_id} not found.") from err

        balance = Balance.objects.filter(customer=customer).first()
        if not balance:
            raise NotFoundError(f"Balance not found for customer {customer_id}.")

        customer.balance = balance

        return customer
