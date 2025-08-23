from rest_framework import serializers

from .enums import CustomerType
from .models import Balance, Customer, Transaction
from .utils import is_valid_cnpj, is_valid_cpf


class CustomerSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
            if (
                attrs.get("type") == CustomerType.INDIVIDUAL
                and not is_valid_cpf(attrs.get("document_number"))
            ):
                raise serializers.ValidationError("Invalid document number (CPF) provided")
            if (
                attrs.get("type") == CustomerType.CORPORATE
                and not is_valid_cnpj(attrs.get("document_number"))
            ):
                raise serializers.ValidationError("Invalid document number (CNPJ) provided")
            if attrs.get("type") not in (CustomerType.INDIVIDUAL, CustomerType.CORPORATE):
                raise serializers.ValidationError("Invalid customer type provided")
            return attrs

    class Meta:
        model = Customer
        fields = ["id", "name", "type", "document_number", "active", "created_at", "updated_at"]
        extra_kwargs = {"document_number": {"write_only": True}}


class BalanceSerializer(serializers.ModelSerializer):
    customer_id = serializers.PrimaryKeyRelatedField(
        queryset=Customer.objects.all(), write_only=True, source="customer"
    )
    customer = CustomerSerializer(read_only=True)

    # TODO: get latest available value on history to calculate the difference

    class Meta:
        model = Balance
        fields = ["id", "customer_id", "customer", "available", "waiting_funds", "updated_at"]


class TransactionSerializer(serializers.ModelSerializer):
    # TODO: get payable customer data

    class Meta:
        model = Transaction
        fields = [
            "id",
            "value",
            "description",
            "method",
            "status",
            "expected_fee",
            "created_at"
        ]
