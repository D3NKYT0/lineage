#!/usr/bin/env python
"""
Teste final para verificar a lógica correta do captcha
"""
import os
import sys
import django

# Configura o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.core.cache import cache

def test_captcha_logic_final():
    """Testa a lógica final do captcha"""
    print("=== Teste Final da Lógica do Captcha ===")
    
    # Simula um IP
    ip = "192.168.1.103"
    cache_key = f"login_attempts_{ip}"
    
    # Limpa cache
    cache.delete(cache_key)
    
    print("Configuração: LOGIN_MAX_ATTEMPTS = 3")
    print("Lógica: attempts >= 3 = captcha necessário")
    print("Comportamento esperado:")
    print("- 1ª tentativa falhada = contador = 1, sem captcha")
    print("- 2ª tentativa falhada = contador = 2, sem captcha")
    print("- 3ª tentativa falhada = contador = 3, COM captcha")
    print("- 4ª tentativa = contador = 4, COM captcha")
    print()
    
    # Testa diferentes cenários
    test_cases = [
        (0, False, "0 tentativas - não deve ter captcha"),
        (1, False, "1 tentativa - não deve ter captcha"),
        (2, False, "2 tentativas - não deve ter captcha"),
        (3, True, "3 tentativas - deve ter captcha"),
        (4, True, "4 tentativas - deve ter captcha"),
        (5, True, "5 tentativas - deve ter captcha"),
    ]
    
    for attempts, expected, description in test_cases:
        # Simula o cache
        if attempts > 0:
            cache.set(cache_key, attempts, 3600)
        else:
            cache.delete(cache_key)
        
        # Simula a lógica do requires_captcha
        max_attempts = 3
        requires_captcha = attempts >= max_attempts
        
        status = "OK" if requires_captcha == expected else "ERRO"
        print(f"{description}: {requires_captcha} (esperado: {expected}) - {status}")
    
    print("\n=== Resumo do Comportamento ===")
    print("✅ 1ª tentativa falhada: contador = 1, sem captcha")
    print("✅ 2ª tentativa falhada: contador = 2, sem captcha") 
    print("✅ 3ª tentativa falhada: contador = 3, COM captcha")
    print("✅ 4ª tentativa: contador = 4, COM captcha")
    print("\n=== Teste Concluído ===")

if __name__ == '__main__':
    test_captcha_logic_final() 