from django.core.management.base import BaseCommand
from apps.main.licence.utils import license_crypto


class Command(BaseCommand):
    help = 'Gera uma nova chave de criptografia para licenças'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Gerando nova chave de criptografia...'))
        
        # Gera uma nova chave
        from apps.main.licence.utils import _get_license_crypto
        new_key = _get_license_crypto().generate_encryption_key()
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('CHAVE DE CRIPTOGRAFIA GERADA'))
        self.stdout.write('='*60)
        self.stdout.write(f'Chave: {new_key}')
        self.stdout.write('\n' + '='*60)
        self.stdout.write('INSTRUÇÕES DE CONFIGURAÇÃO:')
        self.stdout.write('='*60)
        self.stdout.write('1. Adicione a seguinte variável ao seu arquivo .env:')
        self.stdout.write(f'   LICENSE_ENCRYPTION_KEY={new_key}')
        self.stdout.write('\n2. Reinicie o servidor Django')
        self.stdout.write('\n3. A chave será usada para criptografar dados sensíveis')
        self.stdout.write('\n⚠️  IMPORTANTE: Mantenha esta chave segura!')
        self.stdout.write('   Se você perder a chave, não conseguirá descriptografar os dados.') 