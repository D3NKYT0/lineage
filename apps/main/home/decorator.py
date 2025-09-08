from django.contrib.auth.decorators import login_required
from django_otp.decorators import otp_required
from functools import wraps


def conditional_otp_required(view_func):
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        # Verifica se o usuário ativou 2FA e ainda não está verificado via OTP
        if getattr(request.user, 'is_2fa_enabled', False) and not request.user.is_verified():
            return otp_required(view_func)(request, *args, **kwargs)
        return view_func(request, *args, **kwargs)
    return _wrapped_view
