import pytest
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND
from rest_framework.test import APIClient

from payments.enums import TransactionMethod, TransactionStatus


def test_ping_endpoint(best_health_check_ever):
    client = APIClient()
    response = client.get("/ping/")

    assert response.status_code == HTTP_200_OK
    assert response.json() == best_health_check_ever


def test_wrong_endpoint_call():
    client = APIClient()
    response = client.get("/vasco-vai-rebaixar-mais-uma-vez/")

    assert response.status_code == HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_list_transactions(
    credit_transactions_quantity,
    debit_transactions_quantity,
    processed_credit_transactions,
    processed_debit_transactions
):
    client = APIClient()
    response = client.get("/api/v1/payments/transactions/")

    assert response.status_code == HTTP_200_OK
    assert len(response.data) == credit_transactions_quantity + debit_transactions_quantity


@pytest.mark.django_db
@pytest.mark.parametrize("method, expected_count", [
    (TransactionMethod.CREDIT, 6),
    (TransactionMethod.DEBIT, 4)
])
def test_list_transactions_filtered_by_method(
    processed_credit_transactions,
    processed_debit_transactions,
    method,
    expected_count
):
    client = APIClient()
    response = client.get(f"/api/v1/payments/transactions/?method={method}")

    assert response.status_code == HTTP_200_OK
    assert len(response.data) == expected_count


@pytest.mark.django_db
@pytest.mark.parametrize("status, expected_count", [
    (TransactionStatus.PENDING, 1),
    (TransactionStatus.FAILED, 2),
    (TransactionStatus.PROCESSED, 4)
])
def test_list_transactions_filtered_by_status(
    pending_credit_transaction,
    failed_credit_transaction,
    failed_debit_transaction,
    processed_debit_transactions,
    status,
    expected_count
):
    client = APIClient()
    response = client.get(f"/api/v1/payments/transactions/?status={status}")

    assert response.status_code == HTTP_200_OK
    assert len(response.data) == expected_count
