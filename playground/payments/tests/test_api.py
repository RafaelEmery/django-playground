from unittest.mock import patch

import pytest
from factory.faker import Faker
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from rest_framework.test import APIClient

from payments.enums import CustomerType, TransactionMethod, TransactionStatus
from payments.factory import CreditCardTransaction, DebitCardTransaction
from payments.serializers import BalanceSerializer, CustomerSerializer


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


@pytest.mark.django_db
@pytest.mark.parametrize(("customer_type", "document_number", "expected_status_code"), [
    (CustomerType.INDIVIDUAL, "207.227.310-27", HTTP_201_CREATED),
    (CustomerType.INDIVIDUAL, "207.227.310-271", HTTP_400_BAD_REQUEST),
    (CustomerType.CORPORATE, "90.618.336/0001-05", HTTP_201_CREATED),
    (CustomerType.CORPORATE, "90.618.336/0001-051", HTTP_400_BAD_REQUEST),
    (CustomerType.INDIVIDUAL, "90.618.336/0001-05", HTTP_400_BAD_REQUEST),
    (CustomerType.CORPORATE, "207.227.310-27", HTTP_400_BAD_REQUEST),
    ("wrong_customer_type", "207.227.310-27", HTTP_400_BAD_REQUEST)
])
def test_create_customer_and_balance_validating_type_and_document_number(
    customer_type, document_number, expected_status_code
):
    request_data = {
        "name": Faker("name"),
        "type": customer_type,
        "document_number": document_number
    }
    client = APIClient()
    response = client.post("/api/v1/payments/customers/", data=request_data)

    assert response.status_code == expected_status_code


@pytest.mark.django_db
def test_list_customers(individual_customers_quantity, individual_customers):
    client = APIClient()
    response = client.get("/api/v1/payments/customers/")

    assert response.status_code == HTTP_200_OK
    assert len(response.data) == individual_customers_quantity


@pytest.mark.django_db
@pytest.mark.parametrize(("customer_type", "expected_status_code", "expected_quantity"), [
    (CustomerType.INDIVIDUAL, HTTP_200_OK, 5),
    (CustomerType.CORPORATE, HTTP_200_OK, 3),
    ("wrong_customer_type", HTTP_400_BAD_REQUEST, None)
])
def test_list_customers_filtered_by_type(
    individual_customers,
    corporate_customers,
    customer_type,
    expected_status_code,
    expected_quantity
):
    client = APIClient()
    response = client.get(f"/api/v1/payments/customers/?type={customer_type}")

    assert response.status_code == expected_status_code
    if expected_quantity:
        assert len(response.data) == expected_quantity


@pytest.mark.django_db
@pytest.mark.parametrize(("active", "expected_status_code", "expected_quantity"), [
    ("true", HTTP_200_OK, 5),
    ("false", HTTP_200_OK, 1)
])
def test_list_customers_filtered_by_active(
    individual_customers, inactive_customer, active, expected_status_code, expected_quantity
):
    client = APIClient()
    response = client.get(f"/api/v1/payments/customers/?active={active}")

    assert response.status_code == expected_status_code
    assert len(response.data) == expected_quantity


@pytest.mark.django_db
def test_get_customer_by_id(customer):
    client = APIClient()
    response = client.get(f"/api/v1/payments/customers/{customer.id}/")

    expected = CustomerSerializer(customer).data

    assert response.status_code == HTTP_200_OK
    assert response.data == expected


def test_get_customer_by_id_not_found():
    client = APIClient()
    response = client.get("/api/v1/payments/customers/999999/")

    assert response.status_code == HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_delete_customer_with_balance(customer_with_balance):
    client = APIClient()
    response = client.delete(f"/api/v1/payments/customers/{customer_with_balance.id}/")

    assert response.status_code == HTTP_204_NO_CONTENT


def test_delete_customer_with_balance_customer_not_found():
    client = APIClient()
    response = client.delete("/api/v1/payments/customers/999999/")

    assert response.status_code == HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_delete_customer_with_balance_balance_not_found(customer):
    client = APIClient()
    response = client.delete(f"/api/v1/payments/customers/{customer.id}/")

    assert response.status_code == HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_get_balance_by_customer(balance):
    client = APIClient()
    response = client.get(f"/api/v1/payments/customers/{balance.customer.id}/balance/")

    expected = BalanceSerializer(balance).data

    assert response.status_code == HTTP_200_OK
    assert response.data == expected


def test_get_balance_by_customer_not_found():
    client = APIClient()
    response = client.get("/api/v1/payments/customers/999999/balance/")

    assert response.status_code == HTTP_404_NOT_FOUND


@pytest.mark.django_db
@pytest.mark.parametrize("method", [TransactionMethod.CREDIT, TransactionMethod.DEBIT])
def test_process_transaction_success(customer_with_balance, method):
    request_data = {
        "customer_id": customer_with_balance.id,
        "value": 10.0,
        "description": "Em Dezembro de 81, botou os ingleses na roda!",
        "method": method,
        "card_number": "Arrascaeta",
        "card_owner": "Bruno Henrique",
        "card_expiration_year": "2028",
        "card_verification_code": "123",
    }
    client = APIClient()
    response = client.post("/api/v1/payments/transactions/process/", data=request_data)

    assert response.status_code == HTTP_200_OK
    assert response.data["status"] == TransactionStatus.PROCESSED


@pytest.mark.django_db
def test_process_transaction_validation_error(customer_with_balance):
    request_data = {
        "customer_id": customer_with_balance.id,
        "value": 10.0,
        "description": "3 a 0 no Liverpool! Ficou marcado na história!",
        "method": "wrong_method",
        "card_number": "Rodinei",
        "card_owner": "Gabriel Barbosa",
        "card_expiration_year": "2028",
        "card_verification_code": "123",
    }
    client = APIClient()
    response = client.post("/api/v1/payments/transactions/process/", data=request_data)

    assert response.status_code == HTTP_400_BAD_REQUEST


@pytest.mark.django_db
@pytest.mark.parametrize("method", [TransactionMethod.CREDIT, TransactionMethod.DEBIT])
def test_process_transaction_failed_not_found(method):
    request_data = {
        "customer_id": "d9d7729b-dd03-46fe-ae79-bf1c49428efe",
        "value": 10.0,
        "description": "E no Rio não tem outro igual! Só o Flamengo é campeão mundial!",
        "method": method,
        "card_number": "Zico",
        "card_owner": "Leovegildo Júnior",
        "card_expiration_year": "2028",
        "card_verification_code": "123",
    }
    client = APIClient()
    response = client.post("/api/v1/payments/transactions/process/", data=request_data)

    assert response.status_code == HTTP_404_NOT_FOUND


@pytest.mark.django_db
@pytest.mark.parametrize("method", [TransactionMethod.CREDIT, TransactionMethod.DEBIT])
def test_process_transaction_failed_balance_not_found(customer, method):
    request_data = {
        "customer_id": customer.id,
        "value": 10.0,
        "description": "E no Rio não tem outro igual! Só o Flamengo é campeão mundial!",
        "method": method,
        "card_number": "Zico",
        "card_owner": "Leovegildo Júnior",
        "card_expiration_year": "2028",
        "card_verification_code": "123",
    }
    client = APIClient()
    response = client.post("/api/v1/payments/transactions/process/", data=request_data)

    assert response.status_code == HTTP_404_NOT_FOUND


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("method", "factory_class"),
    [
        (TransactionMethod.CREDIT, CreditCardTransaction),
        (TransactionMethod.DEBIT, DebitCardTransaction)
    ]
)
def test_process_transaction_failed_transaction_error(customer_with_balance, method, factory_class):
    request_data = {
        "customer_id": customer_with_balance.id,
        "value": 10.0,
        "description": "E agora seu povo! Pede o mundo de novo! Da-lhe da-lhe da-lhe Mengo! Pra cima deles Flamengo!", # noqa: E501
        "method": method,
        "card_number": "Obina",
        "card_owner": "Adriano Imperador",
        "card_expiration_year": "2028",
        "card_verification_code": "123",
    }
    with patch.object(
        factory_class,
        "apply_payable_on_balance",
        side_effect=Exception("Palmeiras não tem mundial")
    ):
        client = APIClient()
        response = client.post("/api/v1/payments/transactions/process/", data=request_data)

    assert response.status_code == HTTP_500_INTERNAL_SERVER_ERROR
    assert response.data["status"] == TransactionStatus.FAILED
