VALIDADORES_CONQUISTAS = {}


def registrar_validador(codigo):
    def wrapper(func):
        VALIDADORES_CONQUISTAS[codigo] = func
        return func
    return wrapper
