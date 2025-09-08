import base64
import hashlib
import hmac
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from django.conf import settings
import dns.resolver
import time


class LicenseCrypto:
    """
    Utilitário para criptografia de dados de licença
    """
    
    def __init__(self):
        self.encryption_key = self._get_encryption_key()
        try:
            self.cipher_suite = Fernet(self.encryption_key)
        except Exception as e:
            # Se a chave for inválida, gera uma nova baseada no SECRET_KEY
            print(f"Warning: Invalid encryption key, generating new one: {e}")
            self.encryption_key = self._generate_fallback_key()
            self.cipher_suite = Fernet(self.encryption_key)
    
    def _get_encryption_key(self):
        """
        Obtém ou gera a chave de criptografia
        """
        config_key = settings.LICENSE_CONFIG.get('ENCRYPTION_KEY', '')
        
        if config_key:
            # Se a chave está configurada, usa ela
            try:
                # A chave já está em base64, não precisa decodificar
                return config_key.encode()
            except Exception:
                pass
        
        # Se não há chave configurada, gera uma baseada no SECRET_KEY
        return self._generate_fallback_key()
    
    def _generate_fallback_key(self):
        """Gera uma chave baseada no SECRET_KEY do Django"""
        salt = hashlib.sha256(settings.SECRET_KEY.encode()).digest()
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(settings.SECRET_KEY.encode()))
        return key
    
    def encrypt(self, data: str) -> str:
        """
        Criptografa uma string
        """
        if not data:
            return ""
        
        encrypted_data = self.cipher_suite.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted_data).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """
        Descriptografa uma string
        """
        if not encrypted_data:
            return ""
        
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data)
            decrypted_data = self.cipher_suite.decrypt(encrypted_bytes)
            return decrypted_data.decode()
        except Exception:
            return ""
    
    def generate_encryption_key(self) -> str:
        """
        Gera uma nova chave de criptografia
        """
        return Fernet.generate_key().decode()


class LicenseValidator:
    """
    Utilitário para validação de licenças via DNS do denky.dev.br
    """
    
    def __init__(self):
        self.dns_timeout = settings.LICENSE_CONFIG.get('DNS_TIMEOUT', 10)
        self.crypto = LicenseCrypto()

    def validate_contract_via_dns(self, contract_number: str, client_domain: str) -> tuple[bool, str]:
        """
        Valida o número do contrato via registro DNS TXT em denky.dev.br
        """
        # Em modo DEBUG, pula a validação DNS para facilitar desenvolvimento
        if settings.DEBUG:
            return True, "Validação DNS pulada em modo DEBUG"
        
        try:
            # Formata o registro TXT esperado
            txt_record_name = f"pdl-contract-{contract_number}.denky.dev.br"
            
            # Resolve o registro TXT
            resolver = dns.resolver.Resolver()
            resolver.timeout = self.dns_timeout
            resolver.lifetime = self.dns_timeout
            
            answers = resolver.resolve(txt_record_name, 'TXT')
            for answer in answers:
                txt_value = answer.to_text().strip('"')
                # Tenta descriptografar
                try:
                    decrypted_json = self.crypto.decrypt(txt_value)
                    if not decrypted_json:
                        continue
                    import json
                    contract_data = json.loads(decrypted_json)
                    # Confere número do contrato e domínio
                    if contract_data.get('contract_number') == contract_number and contract_data.get('client_domain') == client_domain:
                        return True, "Contrato validado via DNS do denky.dev.br"
                except Exception:
                    continue
            return False, f"Contrato {contract_number} não encontrado ou inválido no registro DNS TXT de {txt_record_name}"
        except dns.resolver.NXDOMAIN:
            return False, f"Registro DNS TXT não encontrado para {txt_record_name}"
        except dns.resolver.NoAnswer:
            return False, f"Nenhum registro TXT encontrado para {txt_record_name}"
        except dns.resolver.Timeout:
            return False, "Timeout na consulta DNS"
        except Exception as e:
            return False, f"Erro na validação DNS: {str(e)}"
    
    def generate_dns_record(self, contract_number: str, domain: str, encrypt: bool = True) -> dict:
        """
        Gera o registro DNS TXT para um contrato
        """
        txt_record_name = f"{self.dns_prefix}.{domain}"
        
        if encrypt:
            txt_value = self.crypto.encrypt(contract_number)
        else:
            txt_value = contract_number
        
        return {
            'name': txt_record_name,
            'type': 'TXT',
            'value': txt_value,
            'ttl': 3600,
            'encrypted': encrypt
        }
    
    def validate_license_key_format(self, license_key: str) -> bool:
        """
        Valida o formato da chave de licença
        """
        if not license_key:
            return False
        
        # Formato esperado: XXXX-XXXX-XXXX-XXXX-XXXX-XXXX-XXXX-XXXX
        parts = license_key.split('-')
        if len(parts) != 8:
            return False
        
        for part in parts:
            if len(part) != 4:
                return False
            if not part.isalnum():
                return False
        
        return True
    
    def generate_license_key(self) -> str:
        """
        Gera uma nova chave de licença
        """
        import secrets
        import string
        
        # Gera uma chave de 32 caracteres
        alphabet = string.ascii_uppercase + string.digits
        key = ''.join(secrets.choice(alphabet) for _ in range(32))
        
        # Formata como XXXX-XXXX-XXXX-XXXX-XXXX-XXXX-XXXX-XXXX
        return '-'.join([key[i:i+4] for i in range(0, 32, 4)])


# Instâncias globais - inicializadas como None para evitar problemas durante importação
license_crypto = None
license_validator = None

def _get_license_crypto():
    """Obtém a instância de LicenseCrypto, criando se necessário"""
    global license_crypto
    if license_crypto is None:
        license_crypto = LicenseCrypto()
    return license_crypto

def _get_license_validator():
    """Obtém a instância de LicenseValidator, criando se necessário"""
    global license_validator
    if license_validator is None:
        license_validator = LicenseValidator()
    return license_validator


def encrypt_license_data(data: str) -> str:
    """
    Função de conveniência para criptografar dados
    """
    return _get_license_crypto().encrypt(data)


def decrypt_license_data(encrypted_data: str) -> str:
    """
    Função de conveniência para descriptografar dados
    """
    return _get_license_crypto().decrypt(encrypted_data)


def validate_contract_dns(contract_number: str, domain: str) -> tuple[bool, str]:
    """
    Função de conveniência para validar contrato via DNS
    """
    return _get_license_validator().validate_contract_via_dns(contract_number, domain)


def generate_dns_record(contract_number: str, domain: str, encrypt: bool = True) -> dict:
    """
    Função de conveniência para gerar registro DNS
    """
    return _get_license_validator().generate_dns_record(contract_number, domain, encrypt) 