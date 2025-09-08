from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse


class SessionLockMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Lista de caminhos que não requerem autenticação
        self.allowed_paths = [
            settings.STATIC_URL,
            settings.MEDIA_URL,
            '/decrypted-file/',
            '/public/',
            '/wiki/',
            '/pages/',
            '/set-language/',
            '/verify/',
            '/components/',
            '/accounts/',
        ]

    def __call__(self, request):
        path = request.path

        # Verifica se o caminho está na lista de caminhos permitidos
        if any(path.startswith(allowed_path) for allowed_path in self.allowed_paths):
            if path == reverse('dashboard'):
                pass
            else:
                return self.get_response(request)
        
        if path == reverse('index'):
            return self.get_response(request)

        # Verifica se o usuário está bloqueado
        locked = request.session.get('is_locked', False)
        is_locked_path = path == reverse('lock')

        if request.user.is_authenticated and locked and not is_locked_path:
            # Usa o parâmetro next como Django faz
            return redirect(f"{reverse('lock')}?next={request.get_full_path()}")

        # Se estiver desbloqueando (na página de lock e não está mais bloqueado)
        if is_locked_path and not locked:
            # Pega a URL de retorno do parâmetro next
            next_url = request.GET.get('next', '/')
            return redirect(next_url)

        return self.get_response(request)
