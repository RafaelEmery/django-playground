from datetime import date
from decimal import Decimal

from factory import Faker, LazyFunction, SubFactory
from factory.django import DjangoModelFactory

from payments.enums import (
    Currency,
    CustomerType,
    PayableStatus,
    TransactionMethod,
    TransactionStatus,
)
from payments.models import Balance, Customer, Payable, Transaction


class TransactionFactory(DjangoModelFactory):
    value = Decimal("100.00")
    currency = Currency.BRL
    description = Faker("sentence")
    method = TransactionMethod.CREDIT
    status = TransactionStatus.PENDING
    expected_fee = Decimal("5.00")
    card_number = Faker("credit_card_number")
    card_owner = Faker("name")
    card_expiration_year = "2028"
    card_verification_code = "123"

    class Meta:
        model = Transaction


class CustomerFactory(DjangoModelFactory):
    name = Faker("name")
    type = CustomerType.INDIVIDUAL
    document_number = Faker("bothify", text="####################")

    class Meta:
        model = Customer


class BalanceFactory(DjangoModelFactory):
    available = 1000.00
    waiting_funds = 0.00
    customer = SubFactory(CustomerFactory)

    class Meta:
        model = Balance


class PayableFactory(DjangoModelFactory):
    amount = 10.0
    customer = SubFactory(CustomerFactory)
    transaction = SubFactory(TransactionFactory)
    status = PayableStatus.WAITING_FUNDS
    payment_date = LazyFunction(date.today)

    class Meta:
        model = Payable
