from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.main.licence.models import License, LicenseVerification
from apps.main.licence.manager import license_manager


class Command(BaseCommand):
    help = 'Verifica o status das licenças PDL'

    def add_arguments(self, parser):
        parser.add_argument(
            '--detailed',
            action='store_true',
            help='Exibe informações detalhadas'
        )
        parser.add_argument(
            '--domain',
            help='Verifica apenas uma licença específica por domínio'
        )

    def handle(self, *args, **options):
        detailed = options['detailed']
        domain_filter = options['domain']

        self.stdout.write(
            self.style.SUCCESS('🔍 Verificando status das licenças PDL...\n')
        )

        # Busca licenças
        if domain_filter:
            licenses = License.objects.filter(domain__icontains=domain_filter)
        else:
            licenses = License.objects.all()

        if not licenses.exists():
            self.stdout.write(
                self.style.WARNING('⚠️ Nenhuma licença encontrada.')
            )
            return

        # Estatísticas gerais
        total_licenses = licenses.count()
        active_licenses = licenses.filter(status='active').count()
        expired_licenses = licenses.filter(status='expired').count()
        suspended_licenses = licenses.filter(status='suspended').count()
        pending_licenses = licenses.filter(status='pending').count()

        self.stdout.write('📊 Estatísticas Gerais:')
        self.stdout.write(f'   Total de licenças: {total_licenses}')
        self.stdout.write(f'   Ativas: {active_licenses}')
        self.stdout.write(f'   Expiradas: {expired_licenses}')
        self.stdout.write(f'   Suspensas: {suspended_licenses}')
        self.stdout.write(f'   Pendentes: {pending_licenses}')
        self.stdout.write('')

        # Licença atual
        current_license = license_manager.get_current_license()
        if current_license:
            self.stdout.write('🎯 Licença Atual:')
            self.stdout.write(f'   Tipo: {current_license.get_license_type_display()}')
            self.stdout.write(f'   Domínio: {current_license.domain}')
            self.stdout.write(f'   Status: {current_license.get_status_display()}')
            self.stdout.write(f'   Ativada em: {current_license.activated_at}')
            if current_license.expires_at:
                self.stdout.write(f'   Expira em: {current_license.expires_at}')
            self.stdout.write(f'   Verificações: {current_license.verification_count}')
            self.stdout.write('')

            # Verifica status atual
            is_valid = license_manager.check_license_status()
            status_icon = '✅' if is_valid else '❌'
            self.stdout.write(f'{status_icon} Status da verificação: {"Válida" if is_valid else "Inválida"}')
            self.stdout.write('')

        # Lista todas as licenças
        if detailed:
            self.stdout.write('📋 Lista de Licenças:')
            for license_obj in licenses:
                self.stdout.write(f'\n🔑 {license_obj.license_key[:12]}...')
                self.stdout.write(f'   Tipo: {license_obj.get_license_type_display()}')
                self.stdout.write(f'   Domínio: {license_obj.domain}')
                self.stdout.write(f'   Empresa: {license_obj.company_name or "Não informado"}')
                self.stdout.write(f'   E-mail: {license_obj.contact_email}')
                self.stdout.write(f'   Status: {license_obj.get_status_display()}')
                self.stdout.write(f'   Ativada em: {license_obj.activated_at}')
                if license_obj.expires_at:
                    self.stdout.write(f'   Expira em: {license_obj.expires_at}')
                self.stdout.write(f'   Verificações: {license_obj.verification_count}')
                self.stdout.write(f'   Criada em: {license_obj.created_at}')
                
                if license_obj.license_type == 'pro':
                    self.stdout.write(f'   Contrato: {license_obj.contract_number or "Não informado"}')
                    self.stdout.write(f'   Suporte usado: {license_obj.support_hours_used}/{license_obj.support_hours_limit} horas')

        # Verificações recentes
        if detailed and current_license:
            recent_verifications = current_license.verifications.all().order_by('-verification_date')[:5]
            if recent_verifications.exists():
                self.stdout.write('\n📈 Verificações Recentes:')
                for verification in recent_verifications:
                    status_icon = '✅' if verification.success else '❌'
                    self.stdout.write(
                        f'   {status_icon} {verification.verification_date.strftime("%d/%m/%Y %H:%M")} - '
                        f'IP: {verification.ip_address} - '
                        f'{verification.response_time:.2f}ms'
                    )
                    if not verification.success and verification.error_message:
                        self.stdout.write(f'      Erro: {verification.error_message}')

        self.stdout.write('\n' + '='*50)
        self.stdout.write(
            self.style.SUCCESS('✅ Verificação concluída!')
        ) 