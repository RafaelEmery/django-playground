# Payments

Simple PSP (Payment Service Provider) based on PagarMe backend developer challenge.

## ER

![payments-er](/images/payments-er.png)

## Endpoints

Defined at Swagger on `http://localhost:8000/swagger/`.

## Processing Transaction

Endpoint: `/api/v1/payments/transactions/process/`

Payload:

```json
{
    "customer_id": "32763849-13cf-4b03-a429-67b65aac8eb8",
    "value": 100.00,
    "description": "Banho da Smell",
    "method": "debit_card",
    "card_number": "1234567890123456",
    "card_owner": "João da Silva",
    "card_expiration_year": "2028",
    "card_verification_code": "123"
}
```

Uses [Factory](https://github.com/RafaelEmery/django-playground/blob/master/playground/payments/factory.py) to define a `credit_card` and `debit_card` transaction :pill:

```python
class Transaction(ABC):
    @abstractmethod
    def create_payable(self, transaction: TransactionModel, customer: Customer) -> Payable:
        pass

    @abstractmethod
    def apply_payable_on_balance(self, payable: Payable, customer: Customer) -> None:
        pass

    @abstractmethod
    def finish_transaction(self, transaction: TransactionModel) -> None:
        pass


class TransactionFactory:
    @staticmethod
    def create(method: str) -> Transaction:
        if method == TransactionMethod.CREDIT:
            return CreditCardTransaction()
        if method == TransactionMethod.DEBIT:
            return DebitCardTransaction()
        else:
            raise ValueError(f"Invalid transaction method: {method}")
```
