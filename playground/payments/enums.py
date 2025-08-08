from django.db import models


class Currency(models.TextChoices):
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


class TransactionMethod(models.TextChoices):
    CREDIT = "credit_card"
    DEBIT = "debit_card"


class Status(models.TextChoices):
    PROCESSED = "processed"
    FAILED = "failed"
    PENDING = "pending"
    WAITING_FUNDS = "waiting_funds"


class CustomerType(models.TextChoices):
    INDIVIDUAL = "individual"
    CORPORATE = "corporate"
