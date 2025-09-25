import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from decimal import Decimal

from django.utils import timezone

from .enums import ExpectedFees, PayableStatus, TransactionMethod, TransactionStatus
from .models import BalanceHistory, Customer, Payable
from .models import Transaction as TransactionModel


class Transaction(ABC):
    @abstractmethod
    def create_payable(self, transaction: TransactionModel, customer: Customer) -> Payable:
        pass

    @abstractmethod
    def apply_payable_on_balance(self, payable: Payable, customer: Customer) -> None:
        pass

    @abstractmethod
    def finish_transaction(self, transaction: TransactionModel) -> None:
        pass

    @abstractmethod
    def fail_transaction(self, transaction: TransactionModel) -> None:
        pass


class TransactionFactory:
    @staticmethod
    def create(method: str) -> Transaction:
        if method == TransactionMethod.CREDIT:
            return CreditCardTransaction()
        if method == TransactionMethod.DEBIT:
            return DebitCardTransaction()
        else:
            raise ValueError(f"Invalid transaction method: {method}")


class CreditCardTransaction(Transaction):
    payable_status: str
    expected_fee: float
    payment_date: datetime

    def __init__(self):
        self.payable_status = PayableStatus.WAITING_FUNDS
        self.expected_fee = ExpectedFees.CREDIT_CARD
        self.payment_date = timezone.now() + timedelta(days=30)

    def create_payable(self, transaction: TransactionModel, customer: Customer) -> Payable:
            calculated_amount = transaction.value - (transaction.value * self.expected_fee)
            return Payable.objects.create(
                transaction=transaction,
                customer=customer,
                status=self.payable_status,
                payment_date=self.payment_date,
                amount=calculated_amount
            )

    def apply_payable_on_balance(self, payable: Payable, customer: Customer) -> None:
        BalanceHistory.objects.create(
            balance=customer.balance,
            available=customer.balance.available,
            waiting_funds=customer.balance.waiting_funds,
        )
        customer.balance.waiting_funds += Decimal(payable.amount)
        customer.balance.save()

    def finish_transaction(self, transaction: TransactionModel) -> None:
        transaction.status = TransactionStatus.PROCESSED
        transaction.expected_fee = self.expected_fee
        transaction.save()

        logging.info(
            f"[payments.factory] transaction {transaction.id} processed as credit_card; "
            f"Fee applied {transaction.expected_fee.value}; "
            f"Payment will be available at {self.payment_date}."
        )

    def fail_transaction(self, transaction: TransactionModel) -> None:
        logging.info(f"[payments.factory] transaction {transaction.id} failed.")

        transaction.status = TransactionStatus.FAILED
        transaction.save()


class DebitCardTransaction(Transaction):
    payable_status: str
    expected_fee: float
    payment_date: datetime

    def __init__(self):
        self.payable_status = PayableStatus.PAID
        self.expected_fee = ExpectedFees.DEBIT_CARD
        self.payment_date = timezone.now()

    def create_payable(self, transaction: TransactionModel, customer: Customer) -> Payable:
        calculated_amount = transaction.value - (transaction.value * self.expected_fee)
        return Payable.objects.create(
            transaction=transaction,
            customer=customer,
            status=self.payable_status,
            payment_date=self.payment_date,
            amount=calculated_amount
        )

    def apply_payable_on_balance(self, payable: Payable, customer: Customer) -> None:
        BalanceHistory.objects.create(
            balance=customer.balance,
            available=customer.balance.available,
            waiting_funds=customer.balance.waiting_funds,
        )
        customer.balance.available += Decimal(payable.amount)
        customer.balance.save()

    def finish_transaction(self, transaction: TransactionModel) -> None:
        transaction.status = TransactionStatus.PROCESSED
        transaction.expected_fee = self.expected_fee
        transaction.save()

        logging.info(
            f"[payments.factory] transaction {transaction.id} processed as debit_card; "
            f"Fee applied {transaction.expected_fee.value}. "
        )

    def fail_transaction(self, transaction: TransactionModel) -> None:
        logging.info(f"[payments.factory] transaction {transaction.id} failed.")

        transaction.status = TransactionStatus.FAILED
        transaction.save()
