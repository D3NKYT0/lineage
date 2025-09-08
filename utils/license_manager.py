import requests
from django.conf import settings

def check_license_status():
    """
    Verifica o status da licença usando o sistema de licença PDL real.
    """
    try:
        # Importa o gerenciador de licenças do PDL
        from apps.main.licence.manager import license_manager
        
        # Verifica o status da licença atual
        is_valid = license_manager.check_license_status()
        
        print(f"[LicenseManager] Status da licença PDL: {'Válida' if is_valid else 'Inválida'}")
        return is_valid
        
    except ImportError as e:
        print(f"[LicenseManager] Erro ao importar sistema de licença: {e}")
        # Se não conseguir importar o sistema de licença, permite o login
        print(f"[LicenseManager] Permitindo login sem verificação de licença")
        return True
        
    except Exception as e:
        print(f"[LicenseManager] Erro ao verificar licença: {e}")
        # Em caso de erro, permite o login para não bloquear o sistema
        print(f"[LicenseManager] Permitindo login devido a erro na verificação de licença")
        return True

def check_license_status_for_testing():
    """
    Versão para testes - permite simular licença inválida
    """
    # Para testes, você pode alterar este valor
    SIMULATE_INVALID_LICENSE = False
    
    if SIMULATE_INVALID_LICENSE:
        print("[LicenseManager] TESTE: Simulando licença inválida")
        return False
    
    return check_license_status() 