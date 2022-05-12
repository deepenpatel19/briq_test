from django.db import models
from briq_test.users.models import User
from briq_test.utils.hash import Hasher

TRANSACTION_CHOICES = (
    ("borrow", "borrow"),
    ("lend", "lend")
)
TRANSACTION_STATUS = (
    ("paid", "paid"),
    ("unpaid", "unpaid")
)


class HashableModel(models.Model):
    """Provide a hash property for models."""
    class Meta:
        abstract = True

    @property
    def hash(self):
        return Hasher.from_model(self)


class Transaction(HashableModel):
    """
    This model stores details related to transaction.
    """
    transaction_id = models.BigAutoField(primary_key=True)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_CHOICES)
    transaction_date = models.DateField()
    transaction_status = models.CharField(max_length=10, choices=TRANSACTION_STATUS)
    transaction_from = models.ForeignKey(User, related_name="transaction_from", on_delete=models.CASCADE)
    transaction_with = models.ForeignKey(User, related_name="transaction_with", on_delete=models.CASCADE)
    transaction_amount = models.FloatField(default=0)
    reason = models.TextField(default="")

    class Meta:
        app_label = "transaction"
