import time
import requests
from django.core.cache import cache
from django.utils import timezone
from django.conf import settings
from .models import License, LicenseVerification
from .utils import license_validator, license_crypto


class LicenseManager:
    """
    Gerenciador central de licenças L2JPremium
    """
    
    def __init__(self):
        self.cache_key = 'current_license'
        self.verification_interval = settings.LICENSE_CONFIG.get('VERIFICATION_INTERVAL', 3600)
        self.cache_timeout = settings.LICENSE_CONFIG.get('CACHE_TIMEOUT', 3600)
    
    def get_current_license(self):
        """
        Obtém a licença ativa atual (com cache)
        """
        # Tenta obter do cache primeiro
        cached_license = cache.get(self.cache_key)
        if cached_license:
            return cached_license
        
        # Busca no banco de dados
        license = License.objects.filter(status='active').first()
        
        if license:
            # Salva no cache
            cache.set(self.cache_key, license, self.cache_timeout)
        
        return license
    
    def check_license_status(self, request=None):
        """
        Verifica se a licença atual é válida
        """
        start_time = time.time()
        current_license = self.get_current_license()
        
        if not current_license:
            self._record_verification(None, request, False, "Nenhuma licença encontrada", start_time)
            return False
        
        try:
            # Verifica se a licença está ativa
            if current_license.status != 'active':
                self._record_verification(current_license, request, False, f"Licença com status: {current_license.status}", start_time)
                # Limpa o cache para garantir que mudanças no admin sejam refletidas
                cache.delete(self.cache_key)
                return False
            
            # Verifica se não expirou (apenas para licenças PRO)
            if current_license.license_type == 'pro' and current_license.expires_at:
                if current_license.expires_at < timezone.now():
                    current_license.status = 'expired'
                    current_license.save()
                    # Limpa o cache após mudança de status
                    cache.delete(self.cache_key)
                    self._record_verification(current_license, request, False, "Licença expirada", start_time)
                    return False
            
            # Verifica se deve fazer verificação remota (desabilitada em desenvolvimento)
            if self._should_verify_remotely(current_license) and not settings.DEBUG:
                remote_valid = self._verify_remotely(current_license, request)
                if not remote_valid:
                    self._record_verification(current_license, request, False, "Falha na verificação remota", start_time)
                    return False
            
            # Atualiza última verificação
            current_license.last_verification = timezone.now()
            current_license.verification_count += 1
            current_license.save()
            
            # Limpa o cache para garantir dados atualizados
            cache.delete(self.cache_key)
            
            self._record_verification(current_license, request, True, "", start_time)
            return True
            
        except Exception as e:
            self._record_verification(current_license, request, False, f"Erro na verificação: {str(e)}", start_time)
            return False
    
    def can_use_feature(self, feature_name, request=None):
        """
        Verifica se a licença permite usar uma funcionalidade específica
        """
        license = self.get_current_license()
        
        if not license:
            return False
        
        if not self.check_license_status(request):
            return False
        
        return license.can_use_feature(feature_name)
    
    def activate_license(self, license_key, domain, contact_email, company_name="", contact_phone=""):
        """
        Ativa uma licença com a chave fornecida
        """
        try:
            license = License.objects.filter(license_key=license_key).first()
            
            if not license:
                return False, "Chave de licença inválida"
            
            if license.status == 'active':
                return False, "Licença já está ativa"
            
            # Ativa a licença
            license.activate(domain)
            license.contact_email = contact_email
            license.company_name = company_name
            license.contact_phone = contact_phone
            license.save()
            
            # Limpa o cache
            cache.delete(self.cache_key)
            
            return True, "Licença ativada com sucesso"
            
        except Exception as e:
            return False, f"Erro ao ativar licença: {str(e)}"
    
    def create_free_license(self, domain, contact_email, company_name="", contact_phone=""):
        """
        Cria uma licença gratuita (L2JPremium FREE) - apenas uma por sistema
        """
        try:
            # Verifica se já existe uma licença FREE ativa
            existing_free = License.objects.filter(license_type='free', status='active').first()
            if existing_free:
                return False, "Já existe uma licença FREE ativa. Apenas uma licença gratuita é permitida por sistema."
            
            # Verifica se já existe uma licença FREE (mesmo inativa)
            existing_free_any = License.objects.filter(license_type='free').first()
            if existing_free_any:
                return False, "Já existe uma licença FREE no sistema. Apenas uma licença gratuita é permitida por sistema."
            
            license = License.objects.create(
                license_type='free',
                domain=domain,
                contact_email=contact_email,
                company_name=company_name,
                contact_phone=contact_phone,
                status='active'
            )
            
            return True, license.id
            
        except Exception as e:
            return False, f"Erro ao criar licença gratuita: {str(e)}"
    
    def validate_contract_via_dns(self, contract_number, domain):
        """
        Valida o número do contrato via registro DNS TXT
        """
        from .utils import _get_license_validator
        return _get_license_validator().validate_contract_via_dns(contract_number, domain)
    
    def create_pro_license(self, domain, contact_email, company_name, contact_phone, contract_number="", skip_dns_validation=False):
        """
        Cria uma licença profissional (L2JPremium PRO) com validação de contrato
        """
        try:
            # Valida se o número do contrato foi fornecido
            if not contract_number:
                return False, "Número do contrato é obrigatório para licenças PRO"

            # Verifica se já existe uma licença com o mesmo número de contrato
            from .models import License
            if License.objects.filter(contract_number=contract_number).exists():
                return False, "Já existe uma licença com este número de contrato. Não é permitido reutilizar o mesmo contrato."

            # Valida o contrato via DNS TXT (a menos que seja pulado)
            if not skip_dns_validation:
                contract_valid, contract_message = self.validate_contract_via_dns(contract_number, domain)
                if not contract_valid:
                    return False, f"Validação de contrato falhou: {contract_message}"
            else:
                print(f"[LicenseManager] Validação DNS pulada para contrato: {contract_number}")

            license = License.objects.create(
                license_type='pro',
                domain=domain,
                contact_email=contact_email,
                company_name=company_name,
                contact_phone=contact_phone,
                contract_number=contract_number,
                status='active',
                expires_at=timezone.now() + timezone.timedelta(days=365)
            )

            return True, license.id

        except Exception as e:
            return False, f"Erro ao criar licença profissional: {str(e)}"
    
    def _should_verify_remotely(self, license):
        """
        Verifica se deve fazer verificação remota baseado no intervalo
        """
        if not license.last_verification:
            return True
        
        time_since_last = timezone.now() - license.last_verification
        return time_since_last.total_seconds() > self.verification_interval
    
    def _verify_remotely(self, license, request):
        """
        Faz verificação remota da licença (simulada por enquanto)
        """
        try:
            # TODO: Implementar verificação real com sua API
            # Por enquanto, simula uma verificação bem-sucedida
            
            # Exemplo de verificação real:
            # response = requests.post(
            #     "https://sua-api-de-licenca.com/verify",
            #     json={
            #         "license_key": license.license_key,
            #         "domain": license.domain,
            #         "timestamp": int(time.time())
            #     },
            #     timeout=10
            # )
            # return response.status_code == 200 and response.json().get("valid", False)
            
            return True
            
        except Exception as e:
            print(f"[LicenseManager] Erro na verificação remota: {e}")
            return False
    
    def _record_verification(self, license, request, success, error_message, start_time):
        """
        Registra uma verificação de licença
        """
        try:
            # Se não há licença, não registra a verificação
            if not license:
                print(f"[LicenseManager] Verificação não registrada: Nenhuma licença disponível")
                return
            
            response_time = (time.time() - start_time) * 1000  # em milissegundos
            
            verification = LicenseVerification(
                license=license,
                success=success,
                error_message=error_message,
                response_time=response_time
            )
            
            if request:
                verification.ip_address = self._get_client_ip(request)
                verification.user_agent = request.META.get('HTTP_USER_AGENT', '')
            else:
                # Se não há request, usa valores padrão
                verification.ip_address = '127.0.0.1'
                verification.user_agent = 'System/CLI'
            
            verification.save()
            
        except Exception as e:
            print(f"[LicenseManager] Erro ao registrar verificação: {e}")
            # Não falha a verificação por causa do erro de registro
    
    def _get_client_ip(self, request):
        """
        Obtém o IP do cliente
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def get_license_info(self):
        """
        Retorna informações da licença atual
        """
        license = self.get_current_license()
        
        if not license:
            return None
        
        return {
            'type': license.get_license_type_display(),
            'status': license.get_status_display(),
            'domain': license.domain,
            'company': license.company_name,
            'contact_email': license.contact_email,
            'activated_at': license.activated_at,
            'expires_at': license.expires_at,
            'features': license.features_enabled,
            'support_hours_used': license.support_hours_used,
            'support_hours_limit': license.support_hours_limit,
        }


# Instância global do gerenciador de licenças
license_manager = LicenseManager()


# Funções de conveniência para compatibilidade com código existente
def check_license_status():
    """
    Função de compatibilidade com o sistema existente
    """
    return license_manager.check_license_status()


def can_use_feature(feature_name):
    """
    Função de conveniência para verificar funcionalidades
    """
    return license_manager.can_use_feature(feature_name) 