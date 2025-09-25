import logging
from decimal import Decimal
from uuid import UUID

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import QuerySet
from django.utils import timezone

from .enums import Currency, PayableStatus, TransactionStatus
from .exceptions import (
    TransactionCreationError,
    TransactionFailedError,
    TransactionRelatedEntityNotFoundError,
)
from .factory import Transaction as TransactionABC
from .factory import TransactionFactory
from .models import Balance, BalanceHistory, Customer, Payable, Transaction


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


class PayableService:
    def get_today_payables(self) -> QuerySet[Payable]:
        today = timezone.now().date()
        payables = Payable.objects.filter(
            created_at__date=today,
            status=PayableStatus.WAITING_FUNDS
        )

        return self._filter_inactive_customer_payables(payables)

    def _filter_inactive_customer_payables(self, payables: Payable) -> QuerySet[Payable]:
        inactive_customer_payables = payables.filter(customer__active=False)
        if inactive_customer_payables:
            inactive_customers = list(
                inactive_customer_payables.values_list("customer_id", flat=True).distinct()
            )
            logging.info(
                "[payments.service] payables for inactive customers are not considered | "
                f"customer_ids: {inactive_customers}"
            )

            return payables.exclude(customer__active=False)
        return payables

    def apply_waiting_funds_payable(self, payable: Payable) -> None:
        balance = payable.customer.balances.first()
        BalanceHistory.objects.create(
            balance=balance,
            available=balance.available,
            waiting_funds=balance.waiting_funds,
        )
        balance.available += Decimal(payable.amount)
        balance.waiting_funds -= Decimal(payable.amount)
        balance.save()

        payable.status = PayableStatus.PAID
        payable.save()

        logging.info(
            f"[payments.service] payable {payable.id} applied for {payable.customer.id}"
        )
