from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from briq_test.users.api.views import UserViewSet
from briq_test.transaction.urls import register_transaction_urls

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("users", UserViewSet)
register_transaction_urls(router)


app_name = "api"
urlpatterns = router.urls
