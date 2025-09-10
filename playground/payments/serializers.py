from rest_framework import serializers

from .enums import CustomerType, TransactionMethod, TransactionStatus
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


class TransactionProcessRequestSerializer(serializers.Serializer):
    """
    Receives and validate transaction process request.
    """
    customer_id = serializers.CharField()
    value = serializers.FloatField(min_value=0.01, max_value=1000000.00)
    description = serializers.CharField(max_length=255)
    method = serializers.ChoiceField(choices=TransactionMethod)
    card_number = serializers.CharField()
    card_owner = serializers.CharField(max_length=100)
    card_expiration_year = serializers.CharField()
    card_verification_code = serializers.CharField(max_length=3)


class TransactionProcessResponseSerializer(serializers.Serializer):
    """
    Returns transaction process response with current status.
    """
    id = serializers.CharField()
    status = serializers.ChoiceField(
        choices=[TransactionStatus.PROCESSED, TransactionStatus.FAILED]
    )
