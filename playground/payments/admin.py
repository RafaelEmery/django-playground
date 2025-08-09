from django.contrib import admin

from .enums import CustomerType, DocumentType
from .models import Customer, Payable, Transaction


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_per_page = 10
    list_display = ["id", "name", "type", "document_type", "document_number", "created_at"]
    search_fields = ["id", "document_number"]
    list_filter = ["type"]

    @admin.display()
    def document_type(self, obj):
        return DocumentType.CPF if obj.type == CustomerType.INDIVIDUAL else DocumentType.CNPJ



@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_per_page = 100
    list_display = [
        "id", "value_with_currency", "method", "expected_fee", "status", "created_at"
    ]
    search_fields = ["id"]
    list_filter = ["method", "status"]
    ordering = ["-created_at"]

    @admin.display()
    def value_with_currency(self, obj):
        return f"{str(obj.value)} {obj.currency}"


@admin.register(Payable)
class PayableAdmin(admin.ModelAdmin):
    list_display = [
        "id", "customer__name", "transaction_details", "status", "created_at", "payment_date"
    ]
    ordering = ["-created_at"]

    @admin.display()
    def transaction_details(self, obj):
        return (
            f"{obj.transaction.id} | "
            f"{obj.transaction.value} {obj.transaction.currency} | "
            f"{obj.transaction.method}"
        )
