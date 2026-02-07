"""
Validação de SQL para Tops Customizados.
Garante que apenas expressões SELECT seguras sejam executadas.
"""
import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


# Padrões perigosos - DDL, DML, comandos de sistema
DANGEROUS_PATTERNS = [
    r'\bINSERT\b', r'\bUPDATE\b', r'\bDELETE\b', r'\bDROP\b',
    r'\bALTER\b', r'\bTRUNCATE\b', r'\bCREATE\b', r'\bEXEC\b',
    r'\bEXECUTE\b', r'\bINTO\b\s+\w+\s+OUTFILE', r'\bLOAD_FILE\b',
    r'\bINFORMATION_SCHEMA\b', r'\bSLEEP\b', r'\bBENCHMARK\b',
    r';\s*', r'--', r'/\*', r'\*/', r'@@', r'@\w+\s*=',
]
DANGEROUS_REGEX = re.compile('|'.join(DANGEROUS_PATTERNS), re.IGNORECASE)


def validate_custom_top_column_sql(value):
    """
    Valida a expressão SQL da coluna extra.
    Permite apenas expressões SELECT (subqueries, colunas, funções).
    """
    if not value or not value.strip():
        raise ValidationError(_("O SQL da coluna não pode estar vazio."))

    value_upper = value.upper().strip()

    if DANGEROUS_REGEX.search(value):
        raise ValidationError(
            _("O SQL contém comandos não permitidos. Use apenas expressões SELECT (ex: subqueries, colunas, funções).")
        )

    # Deve parecer uma expressão de coluna (pode ser subquery, função, etc)
    # Não pode começar com palavras-chave de statement
    statement_starters = ('INSERT', 'UPDATE', 'DELETE', 'DROP', 'ALTER', 'CREATE', 'TRUNCATE')
    first_word = value_upper.split()[0] if value_upper.split() else ''
    if first_word in statement_starters:
        raise ValidationError(_("O SQL não pode iniciar com comando de alteração de dados."))

    # Limite de tamanho razoável
    if len(value) > 1000:
        raise ValidationError(_("O SQL é muito longo. Máximo 1000 caracteres."))

    return value.strip()
