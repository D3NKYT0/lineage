from getpass import getpass
from passlib.hash import bcrypt
from cryptography.fernet import Fernet
# from django.utils.translation import gettext as _


def gerar_chave_fernet():
    """Gera uma chave de 32 bytes (256 bits) compatível com Fernet."""
    return Fernet.generate_key().decode()


def gerar_hash_bcrypt(senha):
    """Gera um hash bcrypt para usar em .htpasswd"""
    return bcrypt.using(rounds=10).hash(senha)


def main():
    print("🔐 Gerador de credenciais")
    senha = getpass("Digite a senha que deseja proteger: ")

    hash_bcrypt = gerar_hash_bcrypt(senha)
    chave_fernet = gerar_chave_fernet()

    print("\n✅ Hash bcrypt (.htpasswd):")
    print(hash_bcrypt)

    print("\n✅ Chave Fernet (settings.py):")
    print(f"ENCRYPTION_KEY = b'{chave_fernet}'")


if __name__ == "__main__":
    main()
