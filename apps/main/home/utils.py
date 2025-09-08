from django.core.exceptions import ValidationError
import re
import os
from django.conf import settings
from core.context_processors import active_theme


def remove_cpf_mask(cpf):
    """
    Remove a máscara do CPF, deixando apenas os números.

    Args:
        cpf (str): CPF no formato com máscara (ex: '123.456.789-09').

    Returns:
        str: CPF sem máscara (ex: '12345678909').
    """
    if not cpf:
        return ""
    return re.sub(r'\D', '', cpf)


def validate_cpf(value):
    """
    Validação de CPF com algoritmo de verificação.
    """
    # Remover caracteres especiais
    cpf = ''.join(filter(str.isdigit, value))
    
    if len(cpf) != 11:
        raise ValidationError('CPF deve ter 11 dígitos')

    if cpf in [str(i)*11 for i in range(10)]:
        raise ValidationError('CPF inválido')
    
    # Validação dos dígitos verificadores
    for i in range(9, 11):
        sum = 0
        for j in range(0, i):
            sum += int(cpf[j]) * ((i+1) - j)
        check_digit = ((sum * 10) % 11) % 10
        if check_digit != int(cpf[i]):
            raise ValidationError('CPF inválido')


def resolve_templated_path(request, base_path, template_name):
    """
    Resolve o caminho do template com base no tema ativo.
    Se existir no tema, retorna esse caminho. Senão, retorna o fallback.
    """
    context_processor_data = active_theme(request)
    theme_slug = context_processor_data.get('theme_slug', '')

    if theme_slug:
        theme_template_path = os.path.join(settings.BASE_DIR, 'themes', 'installed', theme_slug, template_name)
        if os.path.isfile(theme_template_path):
            return f"installed/{theme_slug}/{template_name}"

    return f"{base_path}/{template_name}"
