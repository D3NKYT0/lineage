from django.core.management.base import BaseCommand
from apps.main.licence.manager import license_manager


class Command(BaseCommand):
    help = 'Cria uma licença de teste para verificar o sistema'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🔧 Criando licença de teste...')
        )
        
        try:
            # Cria uma licença FREE de teste
            success, result = license_manager.create_free_license(
                domain='localhost',
                contact_email='teste@L2JPremium.com',
                company_name='L2JPremium Teste',
                contact_phone='(11) 99999-9999'
            )
            
            if success:
                self.stdout.write(
                    self.style.SUCCESS('✅ Licença de teste criada com sucesso!')
                )
                self.stdout.write(f'🔑 Chave: {result}')
                self.stdout.write('🌐 Domínio: localhost')
                self.stdout.write('📧 E-mail: teste@L2JPremium.com')

                # Testa a verificação
                self.stdout.write('\n🔍 Testando verificação...')
                is_valid = license_manager.check_license_status()
                status_icon = '✅' if is_valid else '❌'
                self.stdout.write(f'{status_icon} Status: {"Válida" if is_valid else "Inválida"}')
                
            else:
                self.stdout.write(
                    self.style.ERROR(f'❌ Erro ao criar licença: {result}')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erro inesperado: {str(e)}')
            ) 