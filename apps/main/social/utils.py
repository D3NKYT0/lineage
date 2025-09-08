import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


def validate_cpf(cpf):
    """
    Valida um CPF brasileiro
    """
    # Remove caracteres não numéricos
    cpf = re.sub(r'[^0-9]', '', cpf)
    
    # Verifica se tem 11 dígitos
    if len(cpf) != 11:
        return False
    
    # Verifica se todos os dígitos são iguais
    if cpf == cpf[0] * 11:
        return False
    
    # Calcula o primeiro dígito verificador
    soma = 0
    for i in range(9):
        soma += int(cpf[i]) * (10 - i)
    resto = soma % 11
    if resto < 2:
        digito1 = 0
    else:
        digito1 = 11 - resto
    
    # Calcula o segundo dígito verificador
    soma = 0
    for i in range(10):
        soma += int(cpf[i]) * (11 - i)
    resto = soma % 11
    if resto < 2:
        digito2 = 0
    else:
        digito2 = 11 - resto
    
    # Verifica se os dígitos calculados são iguais aos fornecidos
    return cpf[-2:] == f"{digito1}{digito2}"


def format_cpf(cpf):
    """
    Formata um CPF no padrão XXX.XXX.XXX-XX
    """
    cpf = re.sub(r'[^0-9]', '', cpf)
    if len(cpf) == 11:
        return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
    return cpf


def remove_cpf_mask(cpf):
    """
    Remove a máscara do CPF, deixando apenas os números
    """
    return re.sub(r'[^0-9]', '', cpf)


def validate_phone_number(phone):
    """
    Valida um número de telefone brasileiro
    """
    # Remove caracteres não numéricos
    phone = re.sub(r'[^0-9]', '', phone)
    
    # Verifica se tem entre 10 e 11 dígitos (com DDD)
    if len(phone) < 10 or len(phone) > 11:
        return False
    
    # Verifica se começa com DDD válido (11-99)
    ddd = int(phone[:2])
    if ddd < 11 or ddd > 99:
        return False
    
    return True


def format_phone_number(phone):
    """
    Formata um número de telefone no padrão (XX) XXXXX-XXXX
    """
    phone = re.sub(r'[^0-9]', '', phone)
    if len(phone) == 11:
        return f"({phone[:2]}) {phone[2:7]}-{phone[7:]}"
    elif len(phone) == 10:
        return f"({phone[:2]}) {phone[2:6]}-{phone[6:]}"
    return phone


def get_verification_requirements_status(user):
    """
    Retorna o status dos requisitos para verificação de conta
    """
    return {
        'email_verified': {
            'status': user.is_email_verified,
            'label': _('E-mail verificado'),
            'description': _('Seu e-mail deve estar verificado'),
            'icon': 'bi-envelope-check' if user.is_email_verified else 'bi-envelope-x'
        },
        '2fa_enabled': {
            'status': user.is_2fa_enabled,
            'label': _('2FA habilitado'),
            'description': _('Autenticação de dois fatores deve estar ativa'),
            'icon': 'bi-shield-check' if user.is_2fa_enabled else 'bi-shield-x'
        },
        'account_age': {
            'status': user.date_joined <= timezone.now() - timezone.timedelta(days=30),
            'label': _('Conta com pelo menos 30 dias'),
            'description': _('Sua conta deve ter pelo menos 30 dias de existência'),
            'icon': 'bi-calendar-check' if user.date_joined <= timezone.now() - timezone.timedelta(days=30) else 'bi-calendar-x'
        },
        'activity_level': {
            'status': user.social_posts.count() >= 10,
            'label': _('Pelo menos 10 posts'),
            'description': _('Você deve ter publicado pelo menos 10 posts'),
            'icon': 'bi-chat-dots' if user.social_posts.count() >= 10 else 'bi-chat-x'
        }
    }


def can_request_verification(user):
    """
    Verifica se o usuário pode solicitar verificação
    """
    requirements = get_verification_requirements_status(user)
    
    # Verifica se todos os requisitos foram atendidos
    all_met = all(req['status'] for req in requirements.values())
    
    # Verifica se não há solicitação pendente
    no_pending_request = not user.verification_requests.filter(status='pending').exists()
    
    # Verifica se não está já verificado
    not_already_verified = not user.social_verified
    
    return all_met and no_pending_request and not_already_verified
