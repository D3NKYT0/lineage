from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from apps.main.licence.models import License
from apps.main.licence.manager import license_manager


class Command(BaseCommand):
    help = 'Cria uma nova licença PDL'

    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            choices=['free', 'pro'],
            default='free',
            help='Tipo de licença (free ou pro)'
        )
        parser.add_argument(
            '--domain',
            required=True,
            help='Domínio para ativação'
        )
        parser.add_argument(
            '--email',
            required=True,
            help='E-mail de contato'
        )
        parser.add_argument(
            '--company',
            default='',
            help='Nome da empresa/cliente'
        )
        parser.add_argument(
            '--phone',
            default='',
            help='Telefone de contato'
        )
        parser.add_argument(
            '--contract',
            default='',
            help='Número do contrato (apenas para PDL PRO)'
        )
        parser.add_argument(
            '--days',
            type=int,
            default=365,
            help='Dias de validade (apenas para PDL PRO)'
        )

    def handle(self, *args, **options):
        license_type = options['type']
        domain = options['domain']
        contact_email = options['email']
        company_name = options['company']
        contact_phone = options['phone']
        contract_number = options['contract']
        days = options['days']

        try:
            if license_type == 'free':
                success, result = license_manager.create_free_license(
                    domain, contact_email, company_name, contact_phone
                )
            else:
                success, result = license_manager.create_pro_license(
                    domain, contact_email, company_name, contact_phone, contract_number
                )
            
            if success:
                # Busca a licença criada para exibir informações
                license_obj = License.objects.get(license_key=result)
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ Licença {license_type.upper()} criada com sucesso!'
                    )
                )
                self.stdout.write(f'📋 Chave: {license_obj.license_key}')
                self.stdout.write(f'🌐 Domínio: {license_obj.domain}')
                self.stdout.write(f'📧 E-mail: {license_obj.contact_email}')
                self.stdout.write(f'🏢 Empresa: {license_obj.company_name or "Não informado"}')
                self.stdout.write(f'📞 Telefone: {license_obj.contact_phone or "Não informado"}')
                self.stdout.write(f'📅 Status: {license_obj.get_status_display()}')
                
                if license_type == 'pro':
                    self.stdout.write(f'📄 Contrato: {license_obj.contract_number or "Não informado"}')
                    self.stdout.write(f'⏰ Expira em: {license_obj.expires_at}')
                
                self.stdout.write('\n🔧 Funcionalidades habilitadas:')
                for feature, enabled in license_obj.features_enabled.items():
                    status = '✅' if enabled else '❌'
                    self.stdout.write(f'   {status} {feature}')
                
            else:
                raise CommandError(f'Erro ao criar licença: {result}')
                
        except Exception as e:
            raise CommandError(f'Erro inesperado: {str(e)}') 