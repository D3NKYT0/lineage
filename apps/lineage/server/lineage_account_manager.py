from django.conf import settings

if getattr(settings, 'LINEAGE_ACCOUNT_MODE', 'native') == 'native':
    from utils.dynamic_import import get_query_class
    LineageAccount = get_query_class("LineageAccount")
else:
    import requests

    class LineageAccountAPI:
        @staticmethod
        def check_login_exists(username):
            url = settings.LINEAGE_ACCOUNT_API_URL + 'accounts/dashboard/'
            headers = {'Authorization': f'Token {settings.LINEAGE_ACCOUNT_API_TOKEN}'}
            resp = requests.get(url, headers=headers)
            if resp.status_code == 200:
                return [resp.json().get('account')]
            return []

        @staticmethod
        def update_password(password, username):
            url = settings.LINEAGE_ACCOUNT_API_URL + 'accounts/update_password/'
            headers = {'Authorization': f'Token {settings.LINEAGE_ACCOUNT_API_TOKEN}'}
            data = {'nova_senha': password, 'confirmar_senha': password}
            resp = requests.post(url, json=data, headers=headers)
            return resp.status_code == 200

        @staticmethod
        def register(login, password, access_level, email):
            url = settings.LINEAGE_ACCOUNT_API_URL + 'accounts/register/'
            headers = {'Authorization': f'Token {settings.LINEAGE_ACCOUNT_API_TOKEN}'}
            data = {'password': password, 'confirm': password}
            resp = requests.post(url, json=data, headers=headers)
            return resp.status_code == 200

        @staticmethod
        def link_account_to_user(login, uuid):
            url = settings.LINEAGE_ACCOUNT_API_URL + 'accounts/link/'
            headers = {'Authorization': f'Token {settings.LINEAGE_ACCOUNT_API_TOKEN}'}
            data = {'senha': ''}  # Ajuste conforme necessário
            resp = requests.post(url, json=data, headers=headers)
            return resp.status_code == 200

        @staticmethod
        def validate_credentials(login, senha):
            # Não há endpoint direto, normalmente feito via link
            # Implemente se necessário na API
            return True

        @staticmethod
        def find_accounts_by_email(email):
            url = settings.LINEAGE_ACCOUNT_API_URL + 'accounts/request_link/'
            headers = {'Authorization': f'Token {settings.LINEAGE_ACCOUNT_API_TOKEN}'}
            data = {'email': email}
            resp = requests.post(url, json=data, headers=headers)
            if resp.status_code == 200:
                return [resp.json().get('account')]
            return []

        @staticmethod
        def get_account_by_login(login):
            # Reutiliza dashboard
            return LineageAccountAPI.check_login_exists(login)[0] if LineageAccountAPI.check_login_exists(login) else None

        @staticmethod
        def get_account_by_login_and_email(login, email):
            # Não há endpoint direto, normalmente feito via token
            return None

        @staticmethod
        def get_acess_level():
            # Retorna o nome do campo de access level, igual ao nativo
            return 'accessLevel'

    LineageAccount = LineageAccountAPI 