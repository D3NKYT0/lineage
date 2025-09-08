import re
from django.core.exceptions import ValidationError


def validate_ascii_username(value):
    if not re.fullmatch(r'[A-Za-z0-9]+', value):
        raise ValidationError('O nome de usuário deve conter apenas letras e números (sem espaços ou símbolos).')


def validate_ascii_password(value):
    if not re.fullmatch(r'[A-Za-z0-9]+', value):
        raise ValidationError('A senha deve conter apenas letras e números (sem espaços ou símbolos).')

    if len(value) < 6:
        raise ValidationError('A senha deve ter no mínimo 6 caracteres.')

    if not re.search(r'[A-Za-z]', value):
        raise ValidationError('A senha deve conter pelo menos uma letra.')

    if not re.search(r'[0-9]', value):
        raise ValidationError('A senha deve conter pelo menos um número.')
