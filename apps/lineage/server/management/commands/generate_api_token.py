from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

class Command(BaseCommand):
    help = 'Gera ou exibe o token de autenticação DRF para um usuário.'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, required=True, help='Nome de usuário')
        parser.add_argument('--password', type=str, help='Senha do usuário (será criada se não existir)')

    def handle(self, *args, **options):
        username = options['username']
        password = options.get('password')
        User = get_user_model()
        user, created = User.objects.get_or_create(username=username)
        if created:
            if not password:
                self.stderr.write(self.style.ERROR('Usuário criado, mas é necessário fornecer --password para definir a senha.'))
                return
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Usuário {username} criado.'))
        token, _ = Token.objects.get_or_create(user=user)
        self.stdout.write(self.style.SUCCESS(f'Token para {username}: {token.key}')) 