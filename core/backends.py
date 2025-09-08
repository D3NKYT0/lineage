from django.contrib.auth.backends import ModelBackend
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from utils.license_manager import check_license_status
import logging

logger = logging.getLogger(__name__)

class LicenseBackend(ModelBackend):
    """
    Backend de autenticação que verifica a licença do sistema.
    Deve ser executado PRIMEIRO para validar a licença antes de qualquer login.
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Primeiro verifica a licença, depois autentica o usuário
        """
        logger.debug(f"[LicenseBackend] Iniciando autenticação para usuário: {username}")
        
        # 1. Verifica a licença do sistema ANTES de qualquer autenticação
        logger.debug(f"[LicenseBackend] Verificando status da licença...")
        if not check_license_status():
            logger.warning(f"[LicenseBackend] Licença inválida - bloqueando login para usuário: {username}")
            
            # Não mostra mensagem de erro aqui - será tratada na view específica
            # Apenas retorna None para bloquear o login
            return None
        
        logger.debug(f"[LicenseBackend] Licença válida - permitindo autenticação para usuário: {username}")
        
        # 2. Se a licença for válida, chama o backend pai para autenticar
        user = super().authenticate(request, username, password, **kwargs)
        
        # Se a autenticação falhou, retorna None
        if not user:
            logger.debug(f"[LicenseBackend] Autenticação falhou para usuário: {username}")
            # Vamos verificar se o usuário existe mas está inativo
            from django.contrib.auth import get_user_model
            User = get_user_model()
            try:
                inactive_user = User.objects.get(username=username)
                if not inactive_user.is_active:
                    inactive_user._is_inactive_for_suspension = True
                    inactive_user.backend = 'core.backends.LicenseBackend'
                    return inactive_user
            except User.DoesNotExist:
                pass
            
            return None
            
        logger.info(f"[LicenseBackend] Usuário autenticado com sucesso: {user.username} (is_superuser: {user.is_superuser})")
        
        # 3. Verifica se o usuário está ativo
        # Não bloqueia aqui, deixa a view de login tratar as mensagens de suspensão
        if not user.is_active:
            logger.warning(f"[LicenseBackend] Usuário {user.username} está inativo - permitindo autenticação para tratamento na view")
            # Retorna o usuário mesmo inativo para que a view possa tratar a mensagem
            # A view irá verificar is_active e mostrar a mensagem apropriada
            user._is_inactive_for_suspension = True
        
        # 4. Define o backend no usuário para que o Django saiba qual backend foi usado
        user.backend = 'core.backends.LicenseBackend'
        
        # 5. Verificações adicionais para superusuários (se necessário)
        if user.is_superuser:
            logger.debug(f"[LicenseBackend] Usuário é superusuário: {user.username}")
            # Aqui você pode adicionar verificações específicas para superusuários se necessário
        
        return user

    def get_user(self, user_id):
        """
        Recupera um usuário pelo ID
        """
        try:
            user = super().get_user(user_id)
            if user:
                # Define o backend no usuário para que o Django saiba qual backend foi usado
                user.backend = 'core.backends.LicenseBackend'
                logger.debug(f"[LicenseBackend] Usuário recuperado: {user.username}")
            return user
        except Exception as e:
            logger.error(f"[LicenseBackend] Erro ao recuperar usuário {user_id}: {e}")
            return None 
