from rest_framework import permissions
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType


class IsSuperUser(permissions.BasePermission):
    """
    Permissão personalizada que permite acesso apenas para superusers.
    Mais restritiva que IsAdminUser que permite staff users.
    """
    
    def has_permission(self, request, view):
        # Verifica se o usuário está autenticado
        if not request.user.is_authenticated:
            return False
        
        # Verifica se é superuser
        return bool(request.user.is_superuser)


class IsAPIAdmin(permissions.BasePermission):
    """
    Permissão para administradores da API.
    Permite acesso para superusers ou usuários com permissão específica.
    """
    
    def has_permission(self, request, view):
        # Verifica se o usuário está autenticado
        if not request.user.is_authenticated:
            return False
        
        # Superusers sempre têm acesso
        if request.user.is_superuser:
            return True
        
        # Verifica se o usuário tem a permissão específica para API admin
        try:
            content_type = ContentType.objects.get(app_label='api', model='apiendpointtoggle')
            permission = Permission.objects.get(
                content_type=content_type,
                codename='change_apiendpointtoggle'
            )
            return request.user.has_perm('api.change_apiendpointtoggle')
        except (ContentType.DoesNotExist, Permission.DoesNotExist):
            # Se a permissão não existir, apenas superusers têm acesso
            return False


class IsMonitoringAdmin(permissions.BasePermission):
    """
    Permissão para administradores de monitoramento.
    Permite acesso para superusers ou staff users com permissão específica.
    """
    
    def has_permission(self, request, view):
        # Verifica se o usuário está autenticado
        if not request.user.is_authenticated:
            return False
        
        # Superusers sempre têm acesso
        if request.user.is_superuser:
            return True
        
        # Staff users com permissão específica
        if request.user.is_staff:
            try:
                return request.user.has_perm('api.view_apimetrics')
            except:
                return False
        
        return False 