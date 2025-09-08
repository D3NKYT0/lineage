#!/usr/bin/env python3
"""
Script interativo para ativação de licenças L2JPremium
"""

import os
import sys
import django
from pathlib import Path

# Adiciona o diretório raiz ao path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR))

# Configura o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.main.licence.manager import license_manager
from apps.main.licence.models import License


def print_header():
    """Exibe o cabeçalho do script"""
    print("=" * 60)
    print("🔑 L2JPremium - Sistema de Ativação de Licenças")
    print("=" * 60)
    print()


def get_user_input(prompt, required=True, default=""):
    """Obtém entrada do usuário com validação"""
    while True:
        if default:
            user_input = input(f"{prompt} [{default}]: ").strip()
            if not user_input:
                user_input = default
        else:
            user_input = input(f"{prompt}: ").strip()
        
        if required and not user_input:
            print("❌ Este campo é obrigatório!")
            continue
        
        return user_input


def create_free_license():
    """Cria uma licença gratuita"""
    print("\n📋 Criando licença L2JPremium FREE...")
    print("-" * 40)
    
    domain = get_user_input("🌐 Domínio (ex: meusite.com)")
    contact_email = get_user_input("📧 E-mail de contato")
    company_name = get_user_input("🏢 Nome da empresa/cliente", required=False)
    contact_phone = get_user_input("📞 Telefone de contato", required=False)
    
    print("\n⏳ Criando licença...")
    success, result = license_manager.create_free_license(
        domain, contact_email, company_name, contact_phone
    )
    
    if success:
        print("✅ Licença L2JPremium FREE criada com sucesso!")
        print(f"🔑 Chave: {result}")
        return result
    else:
        print(f"❌ Erro ao criar licença: {result}")
        return None


def create_pro_license():
    """Cria uma licença profissional"""
    print("\n📋 Criando licença L2JPremium PRO...")
    print("-" * 40)
    
    domain = get_user_input("🌐 Domínio (ex: meusite.com)")
    contact_email = get_user_input("📧 E-mail de contato")
    company_name = get_user_input("🏢 Nome da empresa/cliente")
    contact_phone = get_user_input("📞 Telefone de contato", required=False)
    contract_number = get_user_input("📄 Número do contrato", required=False)
    
    print("\n⏳ Criando licença...")
    success, result = license_manager.create_pro_license(
        domain, contact_email, company_name, contact_phone, contract_number
    )
    
    if success:
        print("✅ Licença L2JPremium PRO criada com sucesso!")
        print(f"🔑 Chave: {result}")
        return result
    else:
        print(f"❌ Erro ao criar licença: {result}")
        return None


def activate_existing_license():
    """Ativa uma licença existente"""
    print("\n📋 Ativando licença existente...")
    print("-" * 40)
    
    license_key = get_user_input("🔑 Chave da licença")
    domain = get_user_input("🌐 Domínio para ativação")
    contact_email = get_user_input("📧 E-mail de contato")
    company_name = get_user_input("🏢 Nome da empresa/cliente", required=False)
    contact_phone = get_user_input("📞 Telefone de contato", required=False)
    
    print("\n⏳ Ativando licença...")
    success, result = license_manager.activate_license(
        license_key, domain, contact_email, company_name, contact_phone
    )
    
    if success:
        print("✅ Licença ativada com sucesso!")
        print(f"📝 {result}")
        return True
    else:
        print(f"❌ Erro ao ativar licença: {result}")
        return False


def show_license_info():
    """Exibe informações da licença atual"""
    print("\n📊 Informações da Licença Atual")
    print("-" * 40)
    
    current_license = license_manager.get_current_license()
    if current_license:
        print(f"🔑 Chave: {current_license.license_key}")
        print(f"📋 Tipo: {current_license.get_license_type_display()}")
        print(f"🌐 Domínio: {current_license.domain}")
        print(f"🏢 Empresa: {current_license.company_name or 'Não informado'}")
        print(f"📧 E-mail: {current_license.contact_email}")
        print(f"📞 Telefone: {current_license.contact_phone or 'Não informado'}")
        print(f"📅 Status: {current_license.get_status_display()}")
        print(f"🕐 Ativada em: {current_license.activated_at}")
        if current_license.expires_at:
            print(f"⏰ Expira em: {current_license.expires_at}")
        print(f"🔍 Verificações: {current_license.verification_count}")
        
        if current_license.license_type == 'pro':
            print(f"📄 Contrato: {current_license.contract_number or 'Não informado'}")
            print(f"⏱️ Suporte: {current_license.support_hours_used}/{current_license.support_hours_limit} horas")
        
        # Verifica status atual
        is_valid = license_manager.check_license_status()
        status_icon = "✅" if is_valid else "❌"
        print(f"{status_icon} Status da verificação: {'Válida' if is_valid else 'Inválida'}")
    else:
        print("⚠️ Nenhuma licença ativa encontrada.")


def main_menu():
    """Menu principal"""
    while True:
        print("\n" + "=" * 40)
        print("🎯 Menu Principal")
        print("=" * 40)
        print("1. 📋 Criar licença L2JPremium FREE")
        print("2. ⭐ Criar licença L2JPremium PRO")
        print("3. 🔑 Ativar licença existente")
        print("4. 📊 Ver informações da licença atual")
        print("5. 🔍 Verificar status da licença")
        print("6. 📋 Listar todas as licenças")
        print("0. 🚪 Sair")
        print("-" * 40)
        
        choice = input("Escolha uma opção: ").strip()
        
        if choice == "1":
            create_free_license()
        elif choice == "2":
            create_pro_license()
        elif choice == "3":
            activate_existing_license()
        elif choice == "4":
            show_license_info()
        elif choice == "5":
            print("\n🔍 Verificando status...")
            is_valid = license_manager.check_license_status()
            status_icon = "✅" if is_valid else "❌"
            print(f"{status_icon} Status: {'Válida' if is_valid else 'Inválida'}")
        elif choice == "6":
            print("\n📋 Listando todas as licenças...")
            licenses = License.objects.all().order_by('-created_at')
            if licenses.exists():
                for i, license_obj in enumerate(licenses, 1):
                    print(f"\n{i}. {license_obj.license_key[:12]}...")
                    print(f"   Tipo: {license_obj.get_license_type_display()}")
                    print(f"   Domínio: {license_obj.domain}")
                    print(f"   Status: {license_obj.get_status_display()}")
                    print(f"   Empresa: {license_obj.company_name or 'Não informado'}")
            else:
                print("⚠️ Nenhuma licença encontrada.")
        elif choice == "0":
            print("\n👋 Até logo!")
            break
        else:
            print("❌ Opção inválida!")


if __name__ == "__main__":
    print_header()
    main_menu() 