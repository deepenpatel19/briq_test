from black import out
from rest_framework import viewsets
from django.http import JsonResponse
from briq_test.utils.hash import Hasher
from rest_framework.decorators import action
from django.db.models import Q, Sum, F, Case, When, FloatField
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from .serializers import TransactionSerializer, TransactionPlainSerializer
from rest_framework.pagination import PageNumberPagination
from .models import Transaction


class TransactionViewSet(viewsets.ViewSet):

    page_size = 10

    @action(detail=False, methods=["GET"])
    def get_transactions(self, request, *args, **kwargs):
        """
        Return all transactions.
        """
        query = Transaction.objects.filter(Q(transaction_from=request.user.id) | Q(
            transaction_with=request.user.id)).values().order_by("-transaction_id")

        paginator = PageNumberPagination()
        paginator.page_size = self.page_size
        result_page = paginator.paginate_queryset(query, request)
        serializer = TransactionPlainSerializer.serialize_data(result_page)
        return paginator.get_paginated_response(serializer)

    @swagger_auto_schema(method="post", request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'user_id': openapi.Schema(type=openapi.TYPE_STRING, description='Id of logged in user.'),
            'transaction_type': openapi.Schema(type=openapi.TYPE_STRING, description='Transaction type should be from borrow or lend.'),
            'transaction_amount': openapi.Schema(type=openapi.TYPE_STRING, description='Amount can be positive or negative'),
            'transaction_date': openapi.Schema(type=openapi.TYPE_STRING, description='Format should be YYYY-MM-DD'),
            'transaction_status': openapi.Schema(type=openapi.TYPE_STRING, description='Transaction status should be from paid or unpaid'),
            'transaction_with': openapi.Schema(type=openapi.TYPE_STRING, description='Id of user you want transaction with.'),
            'reason': openapi.Schema(type=openapi.TYPE_STRING, description='Reason for the transaction'),
        }
    ))
    @action(detail=False, methods=["POST"])
    def add_transaction(self, request, *args, **kwargs):
        """
        Add transaction into database.
        """
        request.data.update({"transaction_from": request.user.id})
        serializer = TransactionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return JsonResponse({"message": "OK"}, status=201)

    @action(detail=True, methods=["PATCH"])
    def mark_paid(self, request, *args, **kwargs):
        """
        Particular transaction will be marked as paid.
        """
        transaction_id_tmp = kwargs.get("pk")
        transaction_id = Hasher.to_object_pk(transaction_id_tmp)
        Transaction.objects.filter(transaction_id=transaction_id).update(transaction_status="paid")
        return JsonResponse({"message": "Success"}, status=204)

    @action(detail=False, methods=["GET"])
    def credit_score(self, request, *args, **kwargs):
        """
        Reeturn credit score of the user.
        """
        amount_borrowed = Transaction.objects.filter(Q(transaction_with=request.user) | Q(transaction_from=request.user)).annotate(total_amount=Sum("transaction_amount")).filter(
            transaction_type="borrow").annotate(total_borrowed=Sum("transaction_amount")).annotate(
                percentage=Case(
                    When(total_amount=0, then=0),
                    default=(F("total_borrowed") * 100) / F("total_amount"),
                    output_field=FloatField()
                )
        ).first()

        amount_lended = Transaction.objects.filter(Q(transaction_with=request.user) | Q(transaction_from=request.user)).annotate(total_amount=Sum("transaction_amount")).filter(
            transaction_type="lend").annotate(total_lended=Sum("transaction_amount")).annotate(
                percentage=Case(
                    When(total_amount=0, then=0),
                    default=(F("total_lended") * 100) / F("total_amount"),
                    output_field=FloatField()
                )
        ).first()

        score_on_amount_borrowed = 0
        score_on_amount_lended = 0

        if amount_borrowed:
            percentange_on_amount_borrowed = amount_borrowed.percentage

            if percentange_on_amount_borrowed > 90:
                score_on_amount_borrowed = 100
            elif 80 < percentange_on_amount_borrowed < 90:
                score_on_amount_borrowed = 200
            elif 70 < percentange_on_amount_borrowed < 80:
                score_on_amount_borrowed = 300
            elif 60 < percentange_on_amount_borrowed < 70:
                score_on_amount_borrowed = 400
            elif 50 < percentange_on_amount_borrowed < 60:
                score_on_amount_borrowed = 500
            elif 40 < percentange_on_amount_borrowed < 50:
                score_on_amount_borrowed = 600
            elif 30 < percentange_on_amount_borrowed < 40:
                score_on_amount_borrowed = 700
            elif 20 < percentange_on_amount_borrowed < 30:
                score_on_amount_borrowed = 800
            elif 10 < percentange_on_amount_borrowed < 20:
                score_on_amount_borrowed = 900
            else:
                score_on_amount_borrowed = 1000

        if amount_lended:
            percentange_on_amount_lended = amount_lended.percentage

            if percentange_on_amount_lended > 90:
                score_on_amount_lended = 2000
            elif 80 < percentange_on_amount_lended < 90:
                score_on_amount_lended = 1900
            elif 70 < percentange_on_amount_lended < 80:
                score_on_amount_lended = 1800
            elif 60 < percentange_on_amount_lended < 70:
                score_on_amount_lended = 1700
            elif 50 < percentange_on_amount_lended < 60:
                score_on_amount_lended = 1600
            elif 40 < percentange_on_amount_lended < 50:
                score_on_amount_lended = 1500
            elif 30 < percentange_on_amount_lended < 40:
                score_on_amount_lended = 1400
            elif 20 < percentange_on_amount_lended < 30:
                score_on_amount_lended = 1300
            elif 10 < percentange_on_amount_lended < 20:
                score_on_amount_lended = 1200
            else:
                score_on_amount_lended = 1100

        return JsonResponse({"message": score_on_amount_borrowed + score_on_amount_lended})
