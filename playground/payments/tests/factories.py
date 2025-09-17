from decimal import Decimal

from factory import Faker, SubFactory
from factory.django import DjangoModelFactory

from payments.enums import Currency, CustomerType, TransactionMethod, TransactionStatus
from payments.models import Balance, Customer, Transaction


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
