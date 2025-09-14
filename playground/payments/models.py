import uuid

from django.db import models

from .enums import Currency, CustomerType, PayableStatus, TransactionMethod, TransactionStatus


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return str(self.id)

class BalanceValues(BaseModel):
    """⚠️ really important comment:
    available and waiting_funds can't be more than 999.999.999,99
    no billionaires are allowed in this software ☠️🖕
    """

    available = models.DecimalField(max_digits=13, decimal_places=2, default=0.0)
    waiting_funds = models.DecimalField(max_digits=13, decimal_places=2, default=0.0)

    class Meta:
        abstract = True

class Transaction(BaseModel):
    value = models.DecimalField(max_digits=9, decimal_places=2)
    currency = models.CharField(choices=Currency, default=Currency.BRL)
    description = models.CharField(max_length=255)
    method = models.CharField(choices=TransactionMethod)
    status = models.CharField(choices=TransactionStatus, default=TransactionStatus.PENDING)
    expected_fee = models.DecimalField(max_digits=4, decimal_places=2)
    card_number = models.CharField(max_length=20)
    card_owner = models.CharField(max_length=100)
    card_expiration_year = models.CharField(max_length=4, null=True) # noqa: DJ001
    card_verification_code = models.CharField(max_length=3)

    class Meta:
        ordering = ["id"]


class Customer(BaseModel):
    name = models.CharField(max_length=255)
    type = models.CharField(choices=CustomerType)
    document_number = models.CharField(max_length=20, unique=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["id"]


class Payable(BaseModel):
    transaction = models.ForeignKey(
        Transaction,
        related_name="payables",
        related_query_name="payable",
        on_delete=models.CASCADE
    )
    amount = models.DecimalField(max_digits=9, decimal_places=2, default=0.0)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    status = models.CharField(choices=PayableStatus)
    payment_date = models.DateTimeField()

    class Meta:
        ordering = ["id"]

class Balance(BalanceValues):
    customer = models.ForeignKey(
        Customer,
        related_name="balances",
        related_query_name="balance",
        on_delete=models.PROTECT
    )

    class Meta:
        ordering = ["id"]


class BalanceHistory(BalanceValues):
    balance = models.ForeignKey(
        Balance,
        related_name="balance_historic",
        related_query_name="balance_history",
        on_delete=models.PROTECT
    )

    class Meta:
        verbose_name = "BalancesHistoric"
