from django.db import connection
from django.db.models.signals import post_migrate
from django.dispatch import receiver
import os

from django.db.models.signals import post_save
from django.contrib.auth.models import User
from .models import PerfilGamer, Conquista


@receiver(post_migrate)
def populate_initial_data(sender, **kwargs):
    if sender.name == 'apps.main.home':  # Verifica se o aplicativo é o seu
        # Caminho para os arquivos SQL
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        state_sql_file = os.path.join(base_dir, 'home/sql', 'home_state.sql')
        city_sql_file = os.path.join(base_dir, 'home/sql', 'home_city.sql')

        with connection.cursor() as cursor:
            # Verifica se a tabela State está vazia e popula se necessário
            cursor.execute("SELECT COUNT(*) FROM home_state;")
            if cursor.fetchone()[0] == 0:
                with open(state_sql_file, 'r', encoding='utf-8') as file:  # Adiciona encoding='utf-8'
                    sql = file.read()
                    cursor.execute(sql)

            # Verifica se a tabela City está vazia e popula se necessário
            cursor.execute("SELECT COUNT(*) FROM home_city;")
            if cursor.fetchone()[0] == 0:
                with open(city_sql_file, 'r', encoding='utf-8') as file:  # Adiciona encoding='utf-8'
                    sql = file.read()
                    cursor.execute(sql)


@receiver(post_save, sender=User)
def criar_perfil_gamer(sender, instance, created, **kwargs):
    if created:
        PerfilGamer.objects.create(user=instance)


@receiver(post_migrate)
def criar_conquistas_iniciais(sender, **kwargs):
    # Cria as conquistas iniciais, caso não existam
    conquistas = [
        {'codigo': 'primeiro_login', 'nome': 'Primeiro Login', 'descricao': 'Realizou o primeiro login no sistema'},
        {'codigo': '10_leiloes', 'nome': '10 Leilões', 'descricao': 'Criou 10 leilões no sistema'},
        {'codigo': 'primeira_solicitacao', 'nome': 'Primeira Solicitação', 'descricao': 'Fez sua primeira solicitação'},
        {'codigo': 'avatar_editado', 'nome': 'Avatar Editado', 'descricao': 'Editou seu avatar pela primeira vez'},
        {'codigo': 'endereco_cadastrado', 'nome': 'Endereço Cadastrado', 'descricao': 'Cadastrou seu endereço'},
        {'codigo': 'email_verificado', 'nome': 'Email Verificado', 'descricao': 'Verificou seu e-mail'},
        {'codigo': '2fa_ativado', 'nome': '2FA Ativado', 'descricao': 'Ativou a autenticação de dois fatores (2FA)'},
        {'codigo': 'idioma_trocado', 'nome': 'Idioma Trocado', 'descricao': 'Alterou o idioma do perfil'},
        {'codigo': 'primeiro_amigo', 'nome': 'Primeiro Amigo', 'descricao': 'Fez seu primeiro pedido de amizade'},
        {'codigo': 'primeiro_amigo_aceito', 'nome': 'Primeiro Amigo Aceito', 'descricao': 'Aceitou seu primeiro pedido de amizade'},
        {'codigo': 'primeira_compra', 'nome': 'Primeira Compra', 'descricao': 'Realizou sua primeira compra na loja'},
        {'codigo': 'primeiro_lance', 'nome': 'Primeiro Lance', 'descricao': 'Realizou seu primeiro lance em um leilão'},
        {'codigo': 'primeiro_cupom', 'nome': 'Primeiro Cupom', 'descricao': 'Aplicou um código promocional pela primeira vez'},
        {'codigo': 'primeiro_pedido_pagamento', 'nome': 'Primeira Contribuição', 'descricao': 'Iniciou sua primeira contribuição para o servidor'},
        {'codigo': 'primeiro_pagamento_concluido', 'nome': 'Patrocinador Oficial', 'descricao': 'Realizou seu primeiro apoio financeiro ao servidor'},
        {'codigo': 'primeira_transferencia_para_o_jogo', 'nome': 'Mestre da Economia', 'descricao': 'Realizou sua primeira transferência de moedas para o personagem no servidor'},
        {'codigo': 'primeira_transferencia_para_jogador', 'nome': 'Aliado Generoso', 'descricao': 'Enviou moedas para outro jogador pela primeira vez'},
        {'codigo': 'primeira_retirada_item', 'nome': 'Caçador de Tesouros', 'descricao': 'Retirou seu primeiro item do jogo para o inventário online'},
        {'codigo': 'primeira_insercao_item', 'nome': 'De Volta à Batalha', 'descricao': 'Inseriu um item do inventário online no servidor pela primeira vez'},
        {'codigo': 'primeira_troca_itens', 'nome': 'Comerciante Astuto', 'descricao': 'Realizou sua primeira troca de item entre personagens'},
        {'codigo': 'nivel_10', 'nome': 'Veterano Iniciante', 'descricao': 'Alcançou o nível 10 no sistema'},
        {'codigo': '50_lances', 'nome': 'Lanceador Experiente', 'descricao': 'Realizou 50 lances em leilões'},
        {'codigo': 'primeiro_vencedor_leilao', 'nome': 'Vencedor de Leilão', 'descricao': 'Venceu seu primeiro leilão'},
        {'codigo': '1000_xp', 'nome': 'Mestre da Experiência', 'descricao': 'Acumulou 1000 pontos de experiência'},
        {'codigo': '100_transacoes', 'nome': 'Mestre das Transações', 'descricao': 'Realizou 100 transações na carteira'},
        {'codigo': 'primeiro_bonus', 'nome': 'Bônus Recebido', 'descricao': 'Recebeu seu primeiro bônus de compra'},
        {'codigo': 'nivel_25', 'nome': 'Veterano Avançado', 'descricao': 'Alcançou o nível 25 no sistema'},
        {'codigo': 'primeira_solicitacao_resolvida', 'nome': 'Problema Resolvido', 'descricao': 'Teve sua primeira solicitação de suporte resolvida'},
        {'codigo': 'colecionador_itens', 'nome': 'Colecionador de Itens', 'descricao': 'Possui 10 ou mais itens no inventário'},
        {'codigo': 'mestre_inventario', 'nome': 'Mestre do Inventário', 'descricao': 'Possui 50 ou mais itens no inventário'},
        {'codigo': 'trocador_incansavel', 'nome': 'Trocador Incansável', 'descricao': 'Realizou 10 ou mais trocas de itens'},
        {'codigo': 'gerenciador_economico', 'nome': 'Gerenciador Econômico', 'descricao': 'Realizou 20 ou mais transferências para o jogo'},
        {'codigo': 'benfeitor_comunitario', 'nome': 'Benfeitor Comunitário', 'descricao': 'Realizou 10 ou mais transferências para outros jogadores'},
        {'codigo': '250_transacoes', 'nome': 'Mestre das Transações', 'descricao': 'Realizou 250 transações na carteira'},
        {'codigo': '500_transacoes', 'nome': 'Expert das Transações', 'descricao': 'Realizou 500 transações na carteira'},
        {'codigo': 'bonus_diario_7dias', 'nome': 'Fiel ao Bônus', 'descricao': 'Recebeu bônus diário por 7 dias consecutivos'},
        {'codigo': 'bonus_diario_30dias', 'nome': 'Viciado no Bônus', 'descricao': 'Recebeu bônus diário por 30 dias consecutivos'},
        {'codigo': 'bonus_mestre', 'nome': 'Mestre dos Bônus', 'descricao': 'Recebeu 10 ou mais bônus'},
        {'codigo': 'bonus_expert', 'nome': 'Expert dos Bônus', 'descricao': 'Recebeu 25 ou mais bônus'},
        {'codigo': 'patrocinador_ouro', 'nome': 'Patrocinador Ouro', 'descricao': 'Realizou 5 ou mais pagamentos aprovados'},
        {'codigo': 'patrocinador_diamante', 'nome': 'Patrocinador Diamante', 'descricao': 'Realizou 10 ou mais pagamentos aprovados'},
        {'codigo': 'comprador_frequente', 'nome': 'Comprador Frequente', 'descricao': 'Realizou 5 ou mais compras na loja'},
        {'codigo': 'comprador_vip', 'nome': 'Comprador VIP', 'descricao': 'Realizou 15 ou mais compras na loja'},
        {'codigo': 'leiloeiro_profissional', 'nome': 'Leiloeiro Profissional', 'descricao': 'Criou 25 ou mais leilões'},
        {'codigo': 'leiloeiro_mestre', 'nome': 'Leiloeiro Mestre', 'descricao': 'Criou 50 ou mais leilões'},
        {'codigo': 'lanceador_profissional', 'nome': 'Lanceador Profissional', 'descricao': 'Realizou 100 ou mais lances'},
        {'codigo': 'lanceador_mestre', 'nome': 'Lanceador Mestre', 'descricao': 'Realizou 200 ou mais lances'},
        {'codigo': 'vencedor_serie', 'nome': 'Vencedor em Série', 'descricao': 'Venceu 3 ou mais leilões'},
        {'codigo': 'vencedor_mestre', 'nome': 'Vencedor Mestre', 'descricao': 'Venceu 10 ou mais leilões'},
        {'codigo': 'cupom_mestre', 'nome': 'Mestre dos Cupons', 'descricao': 'Aplicou 5 ou mais cupons promocionais'},
        {'codigo': 'cupom_expert', 'nome': 'Expert dos Cupons', 'descricao': 'Aplicou 15 ou mais cupons promocionais'},
        {'codigo': 'solicitante_frequente', 'nome': 'Solicitante Frequente', 'descricao': 'Abriu 5 ou mais solicitações de suporte'},
        {'codigo': 'solicitante_expert', 'nome': 'Solicitante Expert', 'descricao': 'Abriu 15 ou mais solicitações de suporte'},
        {'codigo': 'resolvedor_problemas', 'nome': 'Resolvedor de Problemas', 'descricao': 'Teve 3 ou mais solicitações resolvidas'},
        {'codigo': 'resolvedor_mestre', 'nome': 'Resolvedor Mestre', 'descricao': 'Teve 10 ou mais solicitações resolvidas'},
        {'codigo': 'rede_social', 'nome': 'Rede Social', 'descricao': 'Tem 5 ou mais amigos aceitos'},
        {'codigo': 'rede_social_mestre', 'nome': 'Mestre da Rede Social', 'descricao': 'Tem 15 ou mais amigos aceitos'},
        {'codigo': 'nivel_50', 'nome': 'Veterano Experiente', 'descricao': 'Alcançou o nível 50 no sistema'},
        {'codigo': 'nivel_75', 'nome': 'Veterano Mestre', 'descricao': 'Alcançou o nível 75 no sistema'},
        {'codigo': 'nivel_100', 'nome': 'Lenda do Sistema', 'descricao': 'Alcançou o nível 100 no sistema'},
        {'codigo': '5000_xp', 'nome': 'Mestre da Experiência', 'descricao': 'Acumulou 5000 pontos de experiência'},
        {'codigo': '10000_xp', 'nome': 'Lenda da Experiência', 'descricao': 'Acumulou 10000 pontos de experiência'},
    ]

    for conquista in conquistas:
        # Se a conquista ainda não existir, cria uma nova
        if not Conquista.objects.filter(codigo=conquista['codigo']).exists():
            Conquista.objects.create(
                codigo=conquista['codigo'],
                nome=conquista['nome'],
                descricao=conquista['descricao']
            )
