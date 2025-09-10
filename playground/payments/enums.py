from enum import Enum, StrEnum

from django.db.models import TextChoices


class Currency(TextChoices):
    BRL = "BRL", "Brazilian Real"
    USD = "USD", "US Dollar"
    EUR = "EUR", "Euro"
    GBP = "GBP", "British Pound"
    JPY = "JPY", "Japanese Yen"
    AUD = "AUD", "Australian Dollar"
    CAD = "CAD", "Canadian Dollar"
    CHF = "CHF", "Swiss Franc"
    CNY = "CNY", "Chinese Yuan"
    SEK = "SEK", "Swedish Krona"
    NZD = "NZD", "New Zealand Dollar"


class TransactionMethod(TextChoices):
    CREDIT = "credit_card"
    DEBIT = "debit_card"


class TransactionStatus(TextChoices):
    PROCESSED = "processed"
    FAILED = "failed"
    PENDING = "pending"


class PayableStatus(TextChoices):
    PAID = "paid"
    WAITING_FUNDS = "waiting_funds"


class CustomerType(TextChoices):
    INDIVIDUAL = "individual"
    CORPORATE = "corporate"


class DocumentType(StrEnum):
    CPF = "CPF"
    CNPJ = "CNPJ"


class ExpectedFees(float, Enum):
    CREDIT_CARD = 0.05
    DEBIT_CARD = 0.03
