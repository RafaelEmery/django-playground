from decimal import Decimal
from unittest.mock import patch

import pytest

from payments.enums import ExpectedFees, PayableStatus, TransactionStatus
from payments.exceptions import TransactionFailedError
from payments.factory import CreditCardTransaction, DebitCardTransaction
from payments.models import Balance, Transaction, TransactionMethod
from payments.services import TransactionService


@pytest.mark.django_db
@pytest.mark.parametrize(
    "method, expected_fee, expected_payable_status, expected_waiting_funds, expected_available",
    [
        (
            TransactionMethod.CREDIT,
            Decimal(ExpectedFees.CREDIT_CARD),
            PayableStatus.WAITING_FUNDS,
            9.50,
            1000.00,
        ),
        (
            TransactionMethod.DEBIT,
            Decimal(ExpectedFees.DEBIT_CARD),
            PayableStatus.PAID,
            0.00,
            1009.70,
        ),
    ]
)
def test_process_transaction_success(
    customer_with_balance,
    method,
    expected_fee,
    expected_payable_status,
    expected_waiting_funds,
    expected_available,
):
    service = TransactionService()
    result = service.process({
        "customer_id": customer_with_balance.id,
        "value": 10.0,
        "description": "Tu és, time de tradição! Raça, amor e paixão! Ó meu Mengo!",
        "method": method,
        "card_number": "Ronaldo Angelim",
        "card_owner": "Léo Moura",
        "card_expiration_year": "2028",
        "card_verification_code": "123",
    })

    balance = Balance.objects.get(customer=customer_with_balance)
    payables = customer_with_balance.payable_set.all()
    transactions = Transaction.objects.filter(
        id__in=payables.values_list("transaction_id", flat=True)
    ).distinct()
    balance_history = balance.balance_historic.order_by("-created_at").first()
    payable = payables.first()
    transaction = transactions.first()

    assert str(result["customer_id"]) == str(customer_with_balance.id)
    assert payable is not None
    assert balance is not None
    assert balance_history is not None
    assert transaction is not None
    assert transaction.status == TransactionStatus.PROCESSED
    assert transaction.expected_fee == pytest.approx(expected_fee)
    assert payable.status == expected_payable_status
    assert float(balance.waiting_funds) == pytest.approx(expected_waiting_funds)
    assert float(balance.available) == pytest.approx(expected_available)
    assert float(balance_history.waiting_funds) == pytest.approx(0.00)
    assert float(balance_history.available) == pytest.approx(1000.00)


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("method", "factory_class"),
    [
        (TransactionMethod.CREDIT, CreditCardTransaction),
        (TransactionMethod.DEBIT, DebitCardTransaction)
    ]
)
def test_process_transaction_failure(customer_with_balance, method, factory_class):
    service = TransactionService()
    with patch.object(
        factory_class,
        "apply_payable_on_balance",
        side_effect=TransactionFailedError("Arerê! O Vasco vai jogar a série B!")
    ):
        with pytest.raises(TransactionFailedError):
            service.process({
                "customer_id": customer_with_balance.id,
                "value": 10.0,
                "description": "Eu, sempre te amarei! Onde estiver, estarei! Ó meu Mengo!",
                "method": method,
                "card_number": "Júlio César",
                "card_owner": "Petković",
                "card_expiration_year": "2028",
                "card_verification_code": "123",
            })

        payables = customer_with_balance.payable_set.all()
        transactions = Transaction.objects.filter(
            id__in=payables.values_list("transaction_id", flat=True)
        ).distinct()
        transaction = transactions.first()

        assert transaction is not None
        assert transaction.status == TransactionStatus.FAILED
