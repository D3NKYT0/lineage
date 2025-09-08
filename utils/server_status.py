"""
Módulo para verificação de status do servidor de jogo
Baseado no sistema do site PHP original
"""

import socket
import os
from typing import Dict, Optional, Tuple
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class ServerStatusChecker:
    """
    Classe para verificar o status do servidor de jogo
    """
    
    def __init__(self):
        self.server_ip = getattr(settings, 'GAME_SERVER_IP', '127.0.0.1')
        self.game_port = int(getattr(settings, 'GAME_SERVER_PORT', 7777))
        self.login_port = int(getattr(settings, 'LOGIN_SERVER_PORT', 2106))
        self.timeout = int(getattr(settings, 'SERVER_STATUS_TIMEOUT', 1))
        self.force_game_status = getattr(settings, 'FORCE_GAME_SERVER_STATUS', 'auto')
        self.force_login_status = getattr(settings, 'FORCE_LOGIN_SERVER_STATUS', 'auto')
    
    def check_port_connection(self, host: str, port: int, timeout: int = None) -> bool:
        """
        Verifica se uma porta está aberta e respondendo
        
        Args:
            host (str): IP ou hostname do servidor
            port (int): Porta a ser verificada
            timeout (int): Timeout em segundos (opcional)
            
        Returns:
            bool: True se a porta estiver aberta, False caso contrário
        """
        if timeout is None:
            timeout = self.timeout
            
        try:
            # Cria um socket TCP
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            
            # Tenta conectar
            result = sock.connect_ex((host, port))
            sock.close()
            
            # Se result == 0, a conexão foi bem-sucedida
            return result == 0
            
        except Exception as e:
            logger.warning(f"Erro ao verificar porta {port} em {host}: {str(e)}")
            return False
    
    def get_game_server_status(self) -> Dict[str, any]:
        """
        Verifica o status do servidor de jogo
        
        Returns:
            Dict com informações do status do servidor
        """
        # Verifica se o status está sendo forçado
        if self.force_game_status == 'on':
            return {
                'status': 'online',
                'forced': True,
                'ip': self.server_ip,
                'port': self.game_port,
                'message': 'Status forçado como online'
            }
        elif self.force_game_status == 'off':
            return {
                'status': 'offline',
                'forced': True,
                'ip': self.server_ip,
                'port': self.game_port,
                'message': 'Status forçado como offline'
            }
        
        # Verificação automática
        is_online = self.check_port_connection(self.server_ip, self.game_port)
        
        return {
            'status': 'online' if is_online else 'offline',
            'forced': False,
            'ip': self.server_ip,
            'port': self.game_port,
            'message': f'Servidor de jogo está {"online" if is_online else "offline"}'
        }
    
    def get_login_server_status(self) -> Dict[str, any]:
        """
        Verifica o status do servidor de login
        
        Returns:
            Dict com informações do status do servidor
        """
        # Verifica se o status está sendo forçado
        if self.force_login_status == 'on':
            return {
                'status': 'online',
                'forced': True,
                'ip': self.server_ip,
                'port': self.login_port,
                'message': 'Status forçado como online'
            }
        elif self.force_login_status == 'off':
            return {
                'status': 'offline',
                'forced': True,
                'ip': self.server_ip,
                'port': self.login_port,
                'message': 'Status forçado como offline'
            }
        
        # Verificação automática
        is_online = self.check_port_connection(self.server_ip, self.login_port)
        
        return {
            'status': 'online' if is_online else 'offline',
            'forced': False,
            'ip': self.server_ip,
            'port': self.login_port,
            'message': f'Servidor de login está {"online" if is_online else "offline"}'
        }
    
    def get_server_status_summary(self) -> Dict[str, any]:
        """
        Retorna um resumo completo do status dos servidores
        
        Returns:
            Dict com status de ambos os servidores
        """
        game_status = self.get_game_server_status()
        login_status = self.get_login_server_status()
        
        # Determina o status geral
        if game_status['status'] == 'online' and login_status['status'] == 'online':
            overall_status = 'online'
        elif game_status['status'] == 'offline' and login_status['status'] == 'offline':
            overall_status = 'offline'
        else:
            overall_status = 'partial'  # Um servidor online, outro offline
        
        return {
            'overall_status': overall_status,
            'game_server': game_status,
            'login_server': login_status,
            'server_ip': self.server_ip,
            'checked_at': self._get_current_timestamp()
        }
    
    def _get_current_timestamp(self) -> str:
        """Retorna timestamp atual formatado"""
        from django.utils import timezone
        return timezone.now().isoformat()


# Funções utilitárias para uso direto
def check_server_status() -> Dict[str, any]:
    """
    Função utilitária para verificar status do servidor
    
    Returns:
        Dict com informações do status
    """
    checker = ServerStatusChecker()
    return checker.get_server_status_summary()


def is_game_server_online() -> bool:
    """
    Função utilitária para verificar se o servidor de jogo está online
    
    Returns:
        bool: True se online, False se offline
    """
    checker = ServerStatusChecker()
    status = checker.get_game_server_status()
    return status['status'] == 'online'


def is_login_server_online() -> bool:
    """
    Função utilitária para verificar se o servidor de login está online
    
    Returns:
        bool: True se online, False se offline
    """
    checker = ServerStatusChecker()
    status = checker.get_login_server_status()
    return status['status'] == 'online'


def check_port(host: str, port: int, timeout: int = 1) -> bool:
    """
    Função utilitária para verificar uma porta específica
    
    Args:
        host (str): IP ou hostname
        port (int): Porta a ser verificada
        timeout (int): Timeout em segundos
        
    Returns:
        bool: True se a porta estiver aberta, False caso contrário
    """
    checker = ServerStatusChecker()
    return checker.check_port_connection(host, port, timeout) 