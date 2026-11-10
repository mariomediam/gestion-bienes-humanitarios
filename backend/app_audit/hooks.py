"""Copy the authenticated login into the open audit context."""


def install_request_login_hook():
    """Wrap APIView.initial once so the login is known before the handler runs."""
    from rest_framework.views import APIView

    if getattr(APIView, '_app_audit_login_hooked', False):
        return

    original_initial = APIView.initial

    def initial(self, request, *args, **kwargs):
        original_initial(self, request, *args, **kwargs)
        from app_audit.context import set_audit_login

        user = getattr(request, 'user', None)
        set_audit_login(getattr(user, 'login', ''))

    APIView.initial = initial
    APIView._app_audit_login_hooked = True
