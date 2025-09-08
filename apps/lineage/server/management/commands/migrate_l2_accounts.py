import os
import secrets
import string
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from apps.lineage.server.database import LineageDB
from utils.dynamic_import import get_query_class

User = get_user_model()


class Command(BaseCommand):
    help = 'Migra contas do banco do L2 para o L2JPremium seguindo regras específicas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Executa em modo de teste sem criar usuários',
        )
        parser.add_argument(
            '--prefix',
            type=str,
            default='L2_',
            help='Prefixo para emails duplicados (padrão: L2_)',
        )
        parser.add_argument(
            '--password-length',
            type=int,
            default=64,
            help='Comprimento da senha aleatória (padrão: 64)',
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='Tamanho do lote para processamento (padrão: 100)',
        )

    def generate_random_password(self, length=64):
        """Gera uma senha aleatória segura"""
        alphabet = string.ascii_letters + string.digits + string.punctuation
        # Remove caracteres problemáticos
        alphabet = alphabet.replace('"', '').replace("'", '').replace('\\', '').replace('`', '')
        return ''.join(secrets.choice(alphabet) for _ in range(length))

    def generate_random_prefix(self, length=6):
        """Gera um prefixo aleatório para emails duplicados"""
        alphabet = string.ascii_uppercase + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))

    def validate_username(self, login):
        """Valida e corrige username se necessário"""
        if not login:
            return None
            
        # Remove caracteres inválidos
        login = ''.join(c for c in login if c.isalnum() or c in '_-')
        
        # Trunca se for muito longo (máximo 16 caracteres)
        if len(login) > 16:
            login = login[:16]
            
        return login if login else None

    def get_l2_accounts(self):
        """Busca contas do L2 com email válido"""
        try:
            sql = """
                SELECT login, 
                       l2email as email,
                       accessLevel, 
                       created_time
                FROM accounts 
                WHERE l2email IS NOT NULL 
                AND l2email != '' 
                AND l2email != 'NULL' 
                AND LENGTH(TRIM(l2email)) > 0
                ORDER BY created_time ASC
            """
            
            accounts = LineageDB().select(sql)
            return accounts
        except Exception as e:
            self.stderr.write(
                self.style.ERROR(f'Erro ao buscar contas do L2: {e}')
            )
            return []

    def check_email_exists(self, email):
        """Verifica se o email já existe no L2JPremium"""
        return User.objects.filter(email=email).exists()

    def check_username_exists(self, username):
        """Verifica se o username já existe no L2JPremium"""
        return User.objects.filter(username=username).exists()

    def create_l2jpremium_user(self, login, email, password, access_level, created_time):
        """Cria usuário no L2JPremium"""
        try:
            # Cria o usuário
            user = User.objects.create_user(
                username=login,
                email=email,
                password=password,
                is_active=True,
                is_email_verified=False,
                is_2fa_enabled=False,
            )
            
            # Define permissões baseadas no access_level do L2
            if access_level is not None and int(access_level) > 0:
                user.is_staff = True
                if int(access_level) >= 100:  # GM ou superior
                    user.is_superuser = True
            
            user.save()
            return True, user
            
        except Exception as e:
            self.stderr.write(
                self.style.ERROR(f'Erro ao criar usuário {login}: {e}')
            )
            return False, None

    def process_accounts(self, l2_accounts, dry_run, prefix, password_length, batch_size):
        """Processa as contas do L2"""
        stats = {
            'total': len(l2_accounts),
            'created': 0,
            'skipped': 0,
            'errors': 0,
            'email_conflicts': 0,
            'l2_duplicates': 0,
            'existing_usernames': 0,
        }

        # Processa emails duplicados dentro do L2
        email_count = {}
        processed_accounts = []
        
        self.stdout.write('🔄 Processando emails duplicados no L2...')
        
        for account in l2_accounts:
            login = account.get('login')
            email = account.get('email')
            access_level = account.get('accessLevel', 0)
            created_time = account.get('created_time')
            
            # Valida dados básicos
            if not login or not email:
                stats['skipped'] += 1
                continue

            # Valida username
            login = self.validate_username(login)
            if not login:
                stats['skipped'] += 1
                continue

            # Trata emails duplicados no L2
            if email in email_count:
                email_count[email] += 1
                random_prefix = self.generate_random_prefix()
                email = f"{random_prefix}_{email}"
                stats['l2_duplicates'] += 1
                if dry_run:
                    self.stdout.write(f'🔄 Email duplicado no L2: {login} → {email}')
            else:
                email_count[email] = 1

            processed_accounts.append({
                'login': login,
                'email': email,
                'access_level': access_level,
                'created_time': created_time
            })

        self.stdout.write(f'✅ Processadas {len(processed_accounts)} contas válidas')

        # Processa em lotes
        self.stdout.write(f'🔄 Iniciando processamento em lotes de {batch_size}...')
        
        for i in range(0, len(processed_accounts), batch_size):
            batch = processed_accounts[i:i + batch_size]
            batch_num = i // batch_size + 1
            total_batches = (len(processed_accounts) + batch_size - 1) // batch_size
            
            self.stdout.write(f'📦 Lote {batch_num}/{total_batches} ({len(batch)} contas)')
            
            for account in batch:
                login = account['login']
                email = account['email']
                access_level = account['access_level']
                created_time = account['created_time']

                # Verifica se username já existe
                if self.check_username_exists(login):
                    stats['existing_usernames'] += 1
                    if dry_run:
                        self.stdout.write(f'⚠️  Username já existe: {login}')
                    stats['skipped'] += 1
                    continue

                # Verifica se email já existe no L2JPremium
                original_email = email
                if self.check_email_exists(email):
                    email = f"{prefix}{email}"
                    stats['email_conflicts'] += 1
                    
                    if self.check_email_exists(email):
                        if dry_run:
                            self.stdout.write(f'⚠️  Email duplicado mesmo com prefixo: {email}')
                        stats['skipped'] += 1
                        continue

                # Gera senha aleatória
                password = self.generate_random_password(password_length)
                
                if dry_run:
                    self.stdout.write(f'🔍 [TESTE] Criaria: {login} → {email}')
                    stats['created'] += 1
                else:
                    # Cria usuário com transação
                    with transaction.atomic():
                        success, user = self.create_l2jpremium_user(
                            login, email, password, access_level, created_time
                        )
                    
                    if success:
                        self.stdout.write(f'✅ Criado: {login} → {email}')
                        stats['created'] += 1
                        
                        # Log da senha para administradores
                        if access_level and int(access_level) > 0:
                            self.stdout.write(f'🔑 Senha para {login}: {password}')
                    else:
                        self.stdout.write(f'❌ Erro ao criar: {login} → {email}')
                        stats['errors'] += 1

        return stats

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        prefix = options['prefix']
        password_length = options['password_length']
        batch_size = options['batch_size']

        self.stdout.write(self.style.SUCCESS('🚀 INICIANDO MIGRAÇÃO L2 → L2JPremium'))

        if dry_run:
            self.stdout.write(self.style.WARNING('⚠️  MODO DE TESTE - Nenhum usuário será criado'))

        # Verifica conexão com L2
        if not LineageDB().is_connected():
            self.stderr.write(self.style.ERROR('❌ Não foi possível conectar ao banco do L2'))
            return

        # Busca contas do L2
        self.stdout.write('📋 Buscando contas do L2...')
        l2_accounts = self.get_l2_accounts()
        
        if not l2_accounts:
            self.stdout.write(self.style.WARNING('⚠️  Nenhuma conta encontrada no L2'))
            return

        self.stdout.write(self.style.SUCCESS(f'✅ Encontradas {len(l2_accounts)} contas no L2'))

        # Processa as contas
        stats = self.process_accounts(l2_accounts, dry_run, prefix, password_length, batch_size)

        # Relatório final
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('📊 RELATÓRIO DE MIGRAÇÃO'))
        self.stdout.write('='*60)
        self.stdout.write(f'Total de contas no L2: {stats["total"]}')
        self.stdout.write(f'Contas válidas processadas: {stats["total"] - stats["skipped"]}')
        self.stdout.write(f'Usuários criados: {stats["created"]}')
        self.stdout.write(f'Pulados: {stats["skipped"]}')
        self.stdout.write(f'Usernames já existentes: {stats["existing_usernames"]}')
        self.stdout.write(f'Erros: {stats["errors"]}')
        self.stdout.write(f'Emails duplicados no L2: {stats["l2_duplicates"]}')
        self.stdout.write(f'Conflitos com L2JPremium resolvidos: {stats["email_conflicts"]}')
        
        if dry_run:
            self.stdout.write('\n⚠️  MODO DE TESTE - Execute sem --dry-run para criar os usuários')
        else:
            self.stdout.write('\n✅ Migração concluída!')
            self.stdout.write('\n📝 PRÓXIMOS PASSOS:')
            self.stdout.write('1. Os usuários precisam definir suas próprias senhas')
            self.stdout.write('2. Eles devem usar a senha do L2 para confirmar a veracidade da conta')
            self.stdout.write('3. As contas não estão vinculadas (conforme solicitado)')
            self.stdout.write('4. Considere enviar emails informativos aos usuários') 