import logging

from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import ListAPIView, ListCreateAPIView
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from rest_framework.views import APIView

from .enums import TransactionStatus
from .models import Balance, Customer, Transaction
from .serializers import (
    BalanceSerializer,
    CustomerSerializer,
    TransactionProcessRequestSerializer,
    TransactionProcessResponseSerializer,
    TransactionSerializer,
)
from .services import TransactionService


class CustomerListCreateAPIView(ListCreateAPIView):
    """
    Return a list of all customers in payments service and
    creates a new customer and balance related.
    Can be filtered by type and active.
    Can be search name.
    Can be ordered by created date.
    """
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ["type", "active"]
    search_fields = ["name"]
    ordering_fields = ["created_at"]

    # TODO: validate and try to set transaction on customer and balance creation
    # TODO: use signals/post_create or post_save function to create balance
    def perform_create(self, serializer):
        """
        Creates a new customer with default balance.
        Perform some validation rules and creates a balance for new customer.
        """
        customer = serializer.save()
        balance_serializer = BalanceSerializer(data={"customer_id": customer.id})
        balance_serializer.is_valid(raise_exception=True)
        balance = balance_serializer.save()

        logging.info(f"[payments] customer created: {customer.id} | balance created: {balance.id}")
        return Response(
            data={"id": customer.id},
            status=HTTP_201_CREATED
        )


class CustomerDetailAPIView(APIView):
    def get(self, request, id):
        customer = get_object_or_404(Customer, id=id)
        serializer = CustomerSerializer(customer)

        return Response(serializer.data)

    # TODO: validate and try to set transaction on customer and balance deletion
    def delete(self, request, id):
        customer = get_object_or_404(Customer, id=id)
        balance = get_object_or_404(Balance, customer=customer)

        logging.info(f"[payments] customer deleted: {customer.id} | balance deleted: {balance.id}")
        balance.delete()
        customer.delete()

        return Response(status=HTTP_204_NO_CONTENT)


class CustomerBalanceAPIView(APIView):
    def get(self, request, id):
        balance = Balance.objects.filter(customer__id=id).first()
        if not balance:
            return Response(
                {"detail": "Balance not found for this customer."},
                status=HTTP_404_NOT_FOUND
            )
        serializer = BalanceSerializer(balance)

        return Response(serializer.data)


class TransactionListAPIView(ListAPIView):
    """
    Return a list of all transactions made in payments service.
    Can be filtered by status, method and expected fee.
    Can be ordered by value and created date.
    """
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["status", "method"]
    ordering_fields = ["value", "created_at"]


class TransactionProcessAPIView(APIView):
    def post(self, request):
        serializer = TransactionProcessRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        logging.info(
            f"[payments] process transaction started: customer {request.data.get('customer_id')}"
        )

        try:
            service = TransactionService()
            result = service.process(data=serializer.validated_data)
            response = TransactionProcessResponseSerializer(result)

            logging.info(
                "[payments] process transaction finished: "
                f"customer_id - {response.data.get('customer_id')} | "
                f"status - {response.data.get('status')}"
            )
        except Exception as e:
            logging.error(
                "[payments] process transaction error: "
                f"customer_id - {request.data.get('customer_id')} | "
                f"error - {str(e)}"
            )
            response = TransactionProcessResponseSerializer(data={
                "customer_id": request.data.get("customer_id"), "status": TransactionStatus.FAILED
            })
            response.is_valid(raise_exception=True)
            return Response(status=HTTP_500_INTERNAL_SERVER_ERROR, data=response.data)

        return Response(status=HTTP_200_OK, data=response.data)



