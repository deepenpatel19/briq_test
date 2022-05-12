from .viewsets import LoginViewSet


def register_authentication_urls(router):
    router.register("login", LoginViewSet, basename="login_custom")
