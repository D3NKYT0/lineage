from django.core.management.base import BaseCommand
from django.utils.translation import gettext_lazy as _
from apps.main.resources.models import SystemResource


class Command(BaseCommand):
    help = 'Popula o banco de dados com os recursos padrão do sistema'

    def handle(self, *args, **options):
        self.stdout.write('Criando recursos padrão do sistema...')
        
        # Recursos da Loja
        shop_resources = [
            {
                'name': 'shop_module',
                'display_name': 'Módulo da Loja',
                'description': 'Sistema completo de loja com itens, pacotes e carrinho',
                'category': 'shop',
                'icon': 'fas fa-shopping-cart',
                'order': 1,
            },
            {
                'name': 'shop_dashboard',
                'display_name': 'Dashboard da Loja',
                'description': 'Painel administrativo da loja',
                'category': 'shop',
                'icon': 'fas fa-tachometer-alt',
                'order': 2,
            },
            {
                'name': 'shop_items',
                'display_name': 'Itens da Loja',
                'description': 'Gerenciamento de itens individuais',
                'category': 'shop',
                'icon': 'fas fa-box',
                'order': 3,
            },
            {
                'name': 'shop_packages',
                'display_name': 'Pacotes da Loja',
                'description': 'Gerenciamento de pacotes de itens',
                'category': 'shop',
                'icon': 'fas fa-gift',
                'order': 4,
            },
            {
                'name': 'shop_cart',
                'display_name': 'Carrinho de Compras',
                'description': 'Sistema de carrinho de compras',
                'category': 'shop',
                'icon': 'fas fa-shopping-basket',
                'order': 5,
            },
            {
                'name': 'shop_checkout',
                'display_name': 'Finalização de Compra',
                'description': 'Processo de checkout e pagamento',
                'category': 'shop',
                'icon': 'fas fa-credit-card',
                'order': 6,
            },
            {
                'name': 'shop_purchases',
                'display_name': 'Histórico de Compras',
                'description': 'Visualização do histórico de compras',
                'category': 'shop',
                'icon': 'fas fa-history',
                'order': 7,
            },
        ]

        # Recursos da Carteira
        wallet_resources = [
            {
                'name': 'wallet_module',
                'display_name': 'Módulo da Carteira',
                'description': 'Sistema de carteira digital',
                'category': 'wallet',
                'icon': 'fas fa-wallet',
                'order': 1,
            },
            {
                'name': 'wallet_dashboard',
                'display_name': 'Dashboard da Carteira',
                'description': 'Painel da carteira digital',
                'category': 'wallet',
                'icon': 'fas fa-chart-line',
                'order': 2,
            },
            {
                'name': 'wallet_transfer',
                'display_name': 'Transferências',
                'description': 'Sistema de transferências entre usuários',
                'category': 'wallet',
                'icon': 'fas fa-exchange-alt',
                'order': 3,
            },
            {
                'name': 'wallet_history',
                'display_name': 'Histórico da Carteira',
                'description': 'Histórico de transações da carteira',
                'category': 'wallet',
                'icon': 'fas fa-list-alt',
                'order': 4,
            },
        ]

        # Recursos da Rede Social
        social_resources = [
            {
                'name': 'social_module',
                'display_name': 'Módulo da Rede Social',
                'description': 'Sistema completo de rede social',
                'category': 'social',
                'icon': 'fas fa-users',
                'order': 1,
            },
            {
                'name': 'social_feed',
                'display_name': 'Feed Social',
                'description': 'Timeline de posts da rede social',
                'category': 'social',
                'icon': 'fas fa-stream',
                'order': 2,
            },
            {
                'name': 'social_profile',
                'display_name': 'Perfis Sociais',
                'description': 'Perfis de usuários na rede social',
                'category': 'social',
                'icon': 'fas fa-user-circle',
                'order': 3,
            },
            {
                'name': 'social_search',
                'display_name': 'Busca Social',
                'description': 'Sistema de busca na rede social',
                'category': 'social',
                'icon': 'fas fa-search',
                'order': 4,
            },
        ]

        # Recursos de Jogos
        games_resources = [
            {
                'name': 'games_module',
                'display_name': 'Módulo de Jogos',
                'description': 'Sistema de jogos e entretenimento',
                'category': 'games',
                'icon': 'fas fa-gamepad',
                'order': 1,
            },
            {
                'name': 'battle_pass',
                'display_name': 'Battle Pass',
                'description': 'Sistema de Battle Pass',
                'category': 'games',
                'icon': 'fas fa-trophy',
                'order': 2,
            },
            {
                'name': 'box_opening',
                'display_name': 'Abertura de Boxes',
                'description': 'Sistema de abertura de caixas',
                'category': 'games',
                'icon': 'fas fa-box-open',
                'order': 3,
            },
            {
                'name': 'roulette',
                'display_name': 'Roleta',
                'description': 'Sistema de roleta de prêmios',
                'category': 'games',
                'icon': 'fas fa-dice',
                'order': 4,
            },
        ]

        # Recursos de Leilões
        auction_resources = [
            {
                'name': 'auction_module',
                'display_name': 'Módulo de Leilões',
                'description': 'Sistema completo de leilões',
                'category': 'auction',
                'icon': 'fas fa-gavel',
                'order': 1,
            },
            {
                'name': 'auction_list',
                'display_name': 'Lista de Leilões',
                'description': 'Visualização de leilões ativos',
                'category': 'auction',
                'icon': 'fas fa-list',
                'order': 2,
            },
            {
                'name': 'auction_create',
                'display_name': 'Criar Leilão',
                'description': 'Criação de novos leilões',
                'category': 'auction',
                'icon': 'fas fa-plus-circle',
                'order': 3,
            },
        ]

        # Recursos do Inventário
        inventory_resources = [
            {
                'name': 'inventory_module',
                'display_name': 'Módulo do Inventário',
                'description': 'Sistema de gerenciamento de inventário',
                'category': 'inventory',
                'icon': 'fas fa-archive',
                'order': 1,
            },
            {
                'name': 'inventory_dashboard',
                'display_name': 'Dashboard do Inventário',
                'description': 'Painel do inventário de personagens',
                'category': 'inventory',
                'icon': 'fas fa-tachometer-alt',
                'order': 2,
            },
        ]

        # Recursos de Pagamentos
        payment_resources = [
            {
                'name': 'payment_module',
                'display_name': 'Módulo de Pagamentos',
                'description': 'Sistema de processamento de pagamentos',
                'category': 'payment',
                'icon': 'fas fa-credit-card',
                'order': 1,
            },
            {
                'name': 'payment_process',
                'display_name': 'Processamento de Pagamentos',
                'description': 'Processamento de transações de pagamento',
                'category': 'payment',
                'icon': 'fas fa-cash-register',
                'order': 2,
            },
            {
                'name': 'payment_history',
                'display_name': 'Histórico de Pagamentos',
                'description': 'Histórico de transações de pagamento',
                'category': 'payment',
                'icon': 'fas fa-receipt',
                'order': 3,
            },
        ]

        # Recursos de Notificações
        notification_resources = [
            {
                'name': 'notification_module',
                'display_name': 'Módulo de Notificações',
                'description': 'Sistema de notificações push e flutuantes',
                'category': 'notification',
                'icon': 'fas fa-bell',
                'order': 1,
            },
        ]

        # Recursos da API
        api_resources = [
            {
                'name': 'api_module',
                'display_name': 'Módulo da API',
                'description': 'Sistema de API REST',
                'category': 'api',
                'icon': 'fas fa-code',
                'order': 1,
            },
        ]

        # Recursos de Administração
        admin_resources = [
            {
                'name': 'admin_module',
                'display_name': 'Módulo de Administração',
                'description': 'Sistema de administração do painel',
                'category': 'admin',
                'icon': 'fas fa-cogs',
                'order': 1,
            },
        ]

        # Combina todos os recursos
        all_resources = (
            shop_resources + wallet_resources + social_resources + 
            games_resources + auction_resources + inventory_resources + 
            payment_resources + notification_resources + api_resources + 
            admin_resources
        )

        created_count = 0
        updated_count = 0

        for resource_data in all_resources:
            resource, created = SystemResource.objects.get_or_create(
                name=resource_data['name'],
                defaults=resource_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Criado: {resource.display_name}')
                )
            else:
                # Atualiza dados se necessário
                updated = False
                for key, value in resource_data.items():
                    if key != 'name' and getattr(resource, key) != value:
                        setattr(resource, key, value)
                        updated = True
                
                if updated:
                    resource.save()
                    updated_count += 1
                    self.stdout.write(
                        self.style.WARNING(f'↻ Atualizado: {resource.display_name}')
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Concluído! {created_count} recursos criados, {updated_count} atualizados.'
            )
        )
