from rest_framework import serializers

from .enums import CustomerType
from .models import Balance, Customer
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
    customer = CustomerSerializer(many=False)
    available_history = serializers.SerializerMethodField()

    # TODO: get latest available value on history to calculate the difference

    class Meta:
        model = Balance
        fields = ["id", "customer", "available", "waiting_funds", "updated_at"]

