from apps.main.home.models import Conquista, ConquistaUsuario
from .validators import VALIDADORES_CONQUISTAS
from apps.lineage.games.utils import verificar_recompensas_por_conquista


def verificar_conquistas(user, request=None):
    conquistas_ganhas = []

    for codigo, func_validadora in VALIDADORES_CONQUISTAS.items():
        conquista = Conquista.objects.filter(codigo=codigo).first()
        if not conquista:
            continue  # ignora se a conquista não existir

        conquista_ja_ganha = ConquistaUsuario.objects.filter(usuario=user, conquista=conquista).exists()

        if not conquista_ja_ganha and func_validadora(user, request=request):
            # ✅ Ganhou agora
            ConquistaUsuario.objects.create(usuario=user, conquista=conquista)
            conquistas_ganhas.append(conquista)

        # ✅ Verifica recompensa SEMPRE, seja nova ou já existente
        verificar_recompensas_por_conquista(user, codigo, request)

    return conquistas_ganhas
