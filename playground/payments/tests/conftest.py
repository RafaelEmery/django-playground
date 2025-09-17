import pytest

from payments.enums import CustomerType, TransactionMethod, TransactionStatus

from .factories import BalanceFactory, CustomerFactory, TransactionFactory


@pytest.fixture
def best_health_check_ever():
    return [
        ["Uma vez Flamengo", "Sempre Flamengo"],
        ["Flamengo sempre, eu hei de ser", "É o meu maior prazer vê-lo brilhar"],
        ["Seja na terra, seja no mar", "Vencer, vencer, vencer!"],
        ["Uma vez Flamengo", "Flamengo até morrer!"],
        ["Na regata, ele me mata, me maltrata, me arrebata", "Que emoção no coração!"],
        ["Consagrado no gramado, sempre amado", "O mais cotado no Fla-Flu é o ai, Jesus!"],
        ["Eu teria um desgosto profundo", "Se faltasse o Flamengo no mundo"],
        ["Ele vibra, ele é fibra muita libra já pesou", "Flamengo até morrer eu sou!"],
        ["Uma vez Flamengo", "Sempre Flamengo"],
        ["Flamengo sempre, eu hei de ser", "É o meu maior prazer vê-lo brilhar"],
        ["Seja na terra, seja no mar", "Vencer, vencer, vencer!"],
        ["Uma vez Flamengo", "Flamengo até morrer!"],
        ["Na regata, ele me mata, me maltrata, me arrebata", "Que emoção no coração!"],
        ["Consagrado no gramado, sempre amado", "O mais cotado no Fla-Flu é o ai, Jesus!"],
        ["Eu teria um desgosto profundo", "Se faltasse o Flamengo no mundo"],
        ["Ele vibra, ele é fibra muita libra já pesou", "Flamengo até morrer eu sou!"]
    ]

@pytest.fixture
def pending_credit_transaction():
    return TransactionFactory()


@pytest.fixture
def processed_credit_transaction():
    return TransactionFactory(status=TransactionStatus.PROCESSED)


@pytest.fixture
def failed_credit_transaction():
    return TransactionFactory(status=TransactionStatus.FAILED)


@pytest.fixture
def pending_debit_transaction():
    return TransactionFactory(method=TransactionMethod.DEBIT)


@pytest.fixture
def processed_debit_transaction():
    return TransactionFactory(
        method=TransactionMethod.DEBIT, status=TransactionStatus.PROCESSED
    )


@pytest.fixture
def failed_debit_transaction():
    return TransactionFactory(
        method=TransactionMethod.DEBIT, status=TransactionStatus.FAILED
    )


@pytest.fixture
def credit_transactions_quantity():
    return 6


@pytest.fixture
def processed_credit_transactions(credit_transactions_quantity):
    return TransactionFactory.create_batch(
        credit_transactions_quantity,
        method=TransactionMethod.CREDIT,
        status=TransactionStatus.PROCESSED
    )


@pytest.fixture
def debit_transactions_quantity():
    return 4


@pytest.fixture
def processed_debit_transactions(debit_transactions_quantity):
    return TransactionFactory.create_batch(
        debit_transactions_quantity,
        method=TransactionMethod.DEBIT,
        status=TransactionStatus.PROCESSED
    )


@pytest.fixture
def individual_customers_quantity():
    return 5


@pytest.fixture
def individual_customers(individual_customers_quantity):
    return CustomerFactory.create_batch(individual_customers_quantity)


@pytest.fixture
def corporate_customers_quantity():
    return 3


@pytest.fixture
def corporate_customers(corporate_customers_quantity):
    return CustomerFactory.create_batch(corporate_customers_quantity, type=CustomerType.CORPORATE)


@pytest.fixture
def customer():
    return CustomerFactory.create()


@pytest.fixture
def customer_with_balance():
    """
    Create a customer with an associated balance.
    With default values for available = 1000.00 and waiting_funds = 0.00
    """
    return BalanceFactory.create().customer


@pytest.fixture
def inactive_customer():
    return CustomerFactory.create(active=False)


@pytest.fixture
def balance():
    return BalanceFactory.create()
