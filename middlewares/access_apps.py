from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import ImproperlyConfigured
from django.urls import resolve

class LoginRequiredAccess:
    """All urls starting with the given prefix require the user to be logged in"""

    LIST_APP_NAME = ['auditor']

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not hasattr(request, 'user'):
            raise ImproperlyConfigured("Requires Django's authentication middleware to be installed.")

        user = request.user
        
        try:
            app_name = resolve(request.path).app_name
        except Exception as e:
            app_name = None

        if app_name in self.LIST_APP_NAME:
            if not user.is_authenticated and not user.is_superuser:
                path = request.get_full_path()
                return redirect_to_login(path)

        return self.get_response(request)
    