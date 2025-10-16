from django.core.management.base import BaseCommand
from apps.licence.models import License
from datetime import datetime, timedelta
import uuid

class Command(BaseCommand):
    help = 'Cria ou lista licenças L2JPremium'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create',
            action='store_true',
            help='Criar uma nova licença de desenvolvimento',
        )
        parser.add_argument(
            '--list',
            action='store_true',
            help='Listar todas as licenças',
        )
        parser.add_argument(
            '--type',
            type=str,
            default='pro',
            choices=['free', 'pro'],
            help='Tipo de licença (free ou pro)',
        )
        parser.add_argument(
            '--domain',
            type=str,
            default='localhost',
            help='Domínio para a licença',
        )
        parser.add_argument(
            '--days',
            type=int,
            default=365,
            help='Dias de validade da licença',
        )

    def handle(self, *args, **options):
        if options['list']:
            self.list_licenses()
        elif options['create']:
            self.create_license(
                license_type=options['type'],
                domain=options['domain'],
                days=options['days']
            )
        else:
            self.stdout.write(
                self.style.WARNING('Use --create para criar ou --list para listar licenças')
            )

    def list_licenses(self):
        """Lista todas as licenças"""
        licenses = License.objects.all().order_by('-created_at')
        
        if not licenses.exists():
            self.stdout.write(self.style.WARNING('Nenhuma licença encontrada.'))
            return

        self.stdout.write(self.style.SUCCESS('\n📋 Licenças existentes:'))
        self.stdout.write('-' * 80)
        
        for license in licenses:
            status_color = self.style.SUCCESS if license.status == 'active' else self.style.ERROR
            
            self.stdout.write(
                f"🔑 {license.contract_number} | "
                f"{license.license_type.upper()} | "
                f"{status_color(license.get_status_display())} | "
                f"{license.domain} | "
                f"Expira: {license.expires_at.strftime('%d/%m/%Y') if license.expires_at else 'N/A'}"
            )

    def create_license(self, license_type, domain, days):
        """Cria uma nova licença"""
        contract_number = f"DEV-{uuid.uuid4().hex[:8].upper()}"
        
        try:
            license = License.objects.create(
                license_type=license_type,
                license_key=f"L2JPREMIUM-{uuid.uuid4().hex.upper()}",
                domain=domain,
                company_name=f'Desenvolvimento - {domain}',
                contact_email=f'dev@{domain}',
                status='active',
                activated_at=datetime.now(),
                expires_at=datetime.now() + timedelta(days=days),
                contract_number=contract_number,
                features_enabled={
                    'can_use_themes': True,
                    'can_use_api': True,
                    'can_use_premium_features': license_type == 'pro',
                    'can_use_custom_branding': license_type == 'pro',
                    'max_concurrent_users': 1000 if license_type == 'pro' else 100,
                    'has_priority_support': license_type == 'pro',
                    'can_use_advanced_analytics': license_type == 'pro',
                    'can_customize_interface': license_type == 'pro'
                },
                notes=f'Licença {license_type.upper()} criada via comando Django'
            )
            
            self.stdout.write(self.style.SUCCESS(f'\n✅ Licença criada com sucesso!'))
            self.stdout.write(f'📋 Contrato: {contract_number}')
            self.stdout.write(f'🔑 Chave: {license.license_key}')
            self.stdout.write(f'🏷️  Tipo: {license_type.upper()}')
            self.stdout.write(f'🌐 Domínio: {domain}')
            self.stdout.write(f'📅 Válida até: {license.expires_at.strftime("%d/%m/%Y %H:%M")}')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erro ao criar licença: {e}'))
