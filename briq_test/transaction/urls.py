from .viewsets import TransactionViewSet


def register_transaction_urls(router):
    router.register("transaction", TransactionViewSet, basename="transaction")
