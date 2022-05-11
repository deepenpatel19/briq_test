from rest_framework import serializers
from briq_test.utils.hash import Hasher
from .models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    transaction_id = serializers.ReadOnlyField(source="hash")

    class Meta:
        model = Transaction
        fields = ("transaction_id", "transaction_type", "transaction_date", "transaction_amount",
                  "transaction_status", "transaction_from", "transaction_with", "reason")


class TransactionPlainSerializer(object):

    @staticmethod
    def serialize_data(queryset):
        """
        Return a list of hashed objects from the given queryset.
        """
        return [
            {
                'transaction_id': Hasher.make_hash(entry.get('transaction_id', None), Transaction),
                'transaction_type': entry.get('transaction_type', None),
                'transaction_date': entry.get('transaction_date', None),
                'transaction_status': entry.get('transaction_status', None),
                'transaction_from': entry.get('transaction_from_id', None),
                'transaction_with': entry.get('transaction_with_id', None),
                'transaction_amount': entry.get('transaction_amount', None),
                'reason': entry.get('reason', None),
            } for entry in queryset
        ]
