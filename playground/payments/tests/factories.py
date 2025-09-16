from decimal import Decimal

from factory import Faker
from factory.django import DjangoModelFactory

from payments.enums import Currency, TransactionMethod, TransactionStatus
from payments.models import Transaction


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
