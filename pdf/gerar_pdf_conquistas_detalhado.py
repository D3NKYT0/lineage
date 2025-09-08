#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import django
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image, Frame, PageTemplate
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import cm
from datetime import datetime
import io

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.main.home.models import Conquista

def create_header_footer(canvas, doc):
    """Cria cabeçalho e rodapé personalizados"""
    canvas.saveState()
    
    # Cabeçalho
    canvas.setFillColor(colors.darkblue)
    canvas.setFont("Helvetica-Bold", 12)
    canvas.drawString(72, A4[1] - 50, "🏆 SISTEMA DE CONQUISTAS")
    
    # Linha decorativa no cabeçalho
    canvas.setStrokeColor(colors.darkblue)
    canvas.setLineWidth(2)
    canvas.line(72, A4[1] - 60, A4[0] - 72, A4[1] - 60)
    
    # Rodapé
    canvas.setFillColor(colors.grey)
    canvas.setFont("Helvetica", 8)
    canvas.drawString(72, 30, f"Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}")
    canvas.drawRightString(A4[0] - 72, 30, f"Página {doc.page}")
    
    # Linha decorativa no rodapé
    canvas.setStrokeColor(colors.grey)
    canvas.setLineWidth(1)
    canvas.line(72, 40, A4[0] - 72, 40)
    
    canvas.restoreState()

def create_achievement_box(conquista, instrucao, categoria_icon):
    """Cria uma caixa estilizada para cada conquista"""
    data = [
        [f"{categoria_icon} {conquista.nome}"],
        [f"📝 {conquista.descricao}"],
        [f"🎯 {instrucao}"]
    ]
    
    table = Table(data, colWidths=[400])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.lightblue, colors.white]),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    
    return table

def create_category_header(categoria_nome, total_conquistas):
    """Cria cabeçalho estilizado para categoria"""
    data = [[f"{categoria_nome} ({total_conquistas} conquistas)"]]
    
    table = Table(data, colWidths=[400])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 15),
        ('TOPPADDING', (0, 0), (-1, 0), 15),
        ('GRID', (0, 0), (-1, -1), 1, colors.darkgreen),
    ]))
    
    return table

def create_progress_bar(conquistas_categoria, total_conquistas):
    """Cria uma barra de progresso visual"""
    progresso = len(conquistas_categoria)
    porcentagem = (progresso / total_conquistas) * 100 if total_conquistas > 0 else 0
    
    # Criar barra de progresso com caracteres ASCII
    barra_completa = 20
    preenchido = int((porcentagem / 100) * barra_completa)
    vazio = barra_completa - preenchido
    
    barra = "█" * preenchido + "░" * vazio
    
    return f"Progresso: {barra} {porcentagem:.1f}% ({progresso}/{total_conquistas})"

def gerar_pdf_conquistas_detalhado():
    """Gera um PDF detalhado com todas as conquistas e instruções específicas"""
    
    # Configurar o documento com template personalizado
    doc = SimpleDocTemplate(
        "Guia_Conquistas_Detalhado.pdf",
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=100,
        bottomMargin=80
    )
    
    # Aplicar template com cabeçalho e rodapé
    template = PageTemplate(id='custom', frames=[Frame(72, 80, A4[0]-144, A4[1]-160)], onPage=create_header_footer)
    doc.addPageTemplates([template])
    
    # Estilos aprimorados
    styles = getSampleStyleSheet()
    
    # Estilo para título principal com gradiente visual
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=28,
        spaceAfter=40,
        alignment=TA_CENTER,
        textColor=colors.darkblue,
        fontName='Helvetica-Bold',
        borderWidth=2,
        borderColor=colors.darkblue,
        borderPadding=20,
        backColor=colors.lightblue
    )
    
    # Estilo para subtítulos com ícones
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=18,
        spaceAfter=15,
        spaceBefore=25,
        textColor=colors.darkgreen,
        fontName='Helvetica-Bold',
        leftIndent=0
    )
    
    # Estilo para descrições com melhor legibilidade
    desc_style = ParagraphStyle(
        'CustomDesc',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=10,
        alignment=TA_JUSTIFY,
        fontName='Helvetica',
        leftIndent=20,
        rightIndent=20,
        backColor=colors.lightgrey,
        borderWidth=1,
        borderColor=colors.grey,
        borderPadding=10
    )
    
    # Estilo para conquistas individuais
    achievement_style = ParagraphStyle(
        'Achievement',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=5,
        spaceBefore=5,
        leftIndent=0,
        fontName='Helvetica'
    )
    
    # Estilo para instruções com destaque
    instruction_style = ParagraphStyle(
        'Instruction',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=8,
        spaceBefore=8,
        leftIndent=30,
        textColor=colors.darkred,
        fontName='Helvetica-Oblique',
        backColor=colors.lightyellow,
        borderWidth=1,
        borderColor=colors.orange,
        borderPadding=5
    )
    
    # Estilo para estratégias
    strategy_style = ParagraphStyle(
        'Strategy',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=12,
        spaceBefore=8,
        leftIndent=20,
        fontName='Helvetica',
        backColor=colors.lightgreen,
        borderWidth=1,
        borderColor=colors.green,
        borderPadding=8
    )
    
    # Estilo para estatísticas
    stats_style = ParagraphStyle(
        'Stats',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=8,
        spaceBefore=8,
        leftIndent=20,
        fontName='Helvetica',
        backColor=colors.lightcyan,
        borderWidth=1,
        borderColor=colors.cyan,
        borderPadding=8
    )
    
    # Conteúdo do PDF
    story = []
    
    # Título principal com design aprimorado
    story.append(Paragraph("🏆 GUIA COMPLETO DE CONQUISTAS", title_style))
    story.append(Spacer(1, 30))
    
    # Introdução com design melhorado
    intro_text = """
    <b>Bem-vindo ao Sistema de Conquistas!</b><br/><br/>
    
    Este guia completo contém todas as conquistas disponíveis no sistema, suas descrições detalhadas e instruções específicas 
    sobre como obtê-las. As conquistas são uma forma de reconhecer suas atividades e progresso no jogo, oferecendo 
    recompensas especiais diretamente para seu inventário!<br/><br/>
    
    <b>Características do Sistema:</b><br/>
    • <b>Recompensas Automáticas:</b> Itens especiais enviados diretamente para seu inventário<br/>
    • <b>Progressão Gradual:</b> Conquistas organizadas por dificuldade e categoria<br/>
    • <b>Reconhecimento Contínuo:</b> Novas conquistas são adicionadas regularmente<br/>
    • <b>Comunidade Ativa:</b> Conquistas que incentivam interação entre jogadores
    """
    story.append(Paragraph(intro_text, desc_style))
    story.append(Spacer(1, 30))
    
    # Dicionário com instruções específicas para cada conquista
    instrucoes_conquistas = {
        # Conquistas de Primeira Vez
        "primeiro_login": "Faça login pela primeira vez no sistema",
        "primeira_solicitacao": "Abra sua primeira solicitação de suporte",
        "avatar_editado": "Edite seu avatar no perfil pela primeira vez",
        "endereco_cadastrado": "Cadastre seu endereço no perfil",
        "email_verificado": "Verifique seu email através do link enviado",
        "2fa_ativado": "Ative a autenticação de dois fatores no perfil",
        "idioma_trocado": "Altere o idioma do sistema no perfil",
        "primeiro_amigo": "Envie seu primeiro pedido de amizade",
        "primeiro_amigo_aceito": "Aceite seu primeiro pedido de amizade",
        "primeira_compra": "Faça sua primeira compra na loja",
        "primeiro_lance": "Faça seu primeiro lance em um leilão",
        "primeiro_cupom": "Aplique um código promocional pela primeira vez",
        "primeiro_pedido_pagamento": "Inicie sua primeira contribuição para o servidor",
        "primeiro_pagamento_concluido": "Complete seu primeiro pagamento de apoio",
        "primeira_transferencia_para_o_jogo": "Transfira moedas para o jogo pela primeira vez",
        "primeira_transferencia_para_jogador": "Envie moedas para outro jogador pela primeira vez",
        "primeira_retirada_item": "Retire um item do jogo para o inventário online",
        "primeira_insercao_item": "Insira um item do inventário online no servidor",
        "primeira_troca_itens": "Realize sua primeira troca de item entre personagens",
        "primeiro_vencedor_leilao": "Vence seu primeiro leilão",
        "primeiro_bonus": "Receba seu primeiro bônus de compra",
        
        # Conquistas de Inventário
        "colecionador_itens": "Acumule 10 ou mais itens no seu inventário",
        "mestre_inventario": "Acumule 50 ou mais itens no seu inventário",
        "trocador_incansavel": "Realize 10 ou mais trocas de itens",
        
        # Conquistas de Carteira
        "gerenciador_economico": "Realize 20 ou mais transferências para o jogo",
        "benfeitor_comunitario": "Realize 10 ou mais transferências para outros jogadores",
        "100_transacoes": "Realize 100 transações na carteira",
        "250_transacoes": "Realize 250 transações na carteira",
        "500_transacoes": "Realize 500 transações na carteira",
        
        # Conquistas de Bônus
        "bonus_diario_7dias": "Receba bônus diário por 7 dias consecutivos",
        "bonus_diario_30dias": "Receba bônus diário por 30 dias consecutivos",
        "bonus_mestre": "Receba 10 ou mais bônus",
        "bonus_expert": "Receba 25 ou mais bônus",
        
        # Conquistas de Patrocínio
        "patrocinador_ouro": "Realize 5 ou mais pagamentos aprovados",
        "patrocinador_diamante": "Realize 10 ou mais pagamentos aprovados",
        
        # Conquistas de Loja
        "comprador_frequente": "Realize 5 ou mais compras na loja",
        "comprador_vip": "Realize 15 ou mais compras na loja",
        
        # Conquistas de Leilões
        "10_leiloes": "Crie 10 leilões no sistema",
        "leiloeiro_profissional": "Crie 25 ou mais leilões",
        "leiloeiro_mestre": "Crie 50 ou mais leilões",
        "50_lances": "Realize 50 lances em leilões",
        "lanceador_profissional": "Realize 100 ou mais lances",
        "lanceador_mestre": "Realize 200 ou mais lances",
        "vencedor_serie": "Vence 3 ou mais leilões",
        "vencedor_mestre": "Vence 10 ou mais leilões",
        
        # Conquistas de Cupons
        "cupom_mestre": "Aplique 5 ou mais cupons promocionais",
        "cupom_expert": "Aplique 15 ou mais cupons promocionais",
        
        # Conquistas de Suporte
        "solicitante_frequente": "Abra 5 ou mais solicitações de suporte",
        "solicitante_expert": "Abra 15 ou mais solicitações de suporte",
        "resolvedor_problemas": "Tenha 3 ou mais solicitações resolvidas",
        "resolvedor_mestre": "Tenha 10 ou mais solicitações resolvidas",
        
        # Conquistas de Rede Social
        "rede_social": "Tenha 5 ou mais amigos aceitos",
        "rede_social_mestre": "Tenha 15 ou mais amigos aceitos",
        
        # Conquistas de Nível
        "nivel_10": "Alcance o nível 10 no sistema",
        "nivel_25": "Alcance o nível 25 no sistema",
        "nivel_50": "Alcance o nível 50 no sistema",
        "nivel_75": "Alcance o nível 75 no sistema",
        "nivel_100": "Alcance o nível 100 no sistema",
        
        # Conquistas de Experiência
        "1000_xp": "Acumule 1000 pontos de experiência",
        "5000_xp": "Acumule 5000 pontos de experiência",
        "10000_xp": "Acumule 10000 pontos de experiência"
    }
    
    # Categorias de conquistas com ícones
    categorias = {
        "🎮 CONQUISTAS DE PRIMEIRA VEZ": [
            "primeiro_login",
            "primeira_solicitacao", 
            "avatar_editado",
            "endereco_cadastrado",
            "email_verificado",
            "2fa_ativado",
            "idioma_trocado",
            "primeiro_amigo",
            "primeiro_amigo_aceito",
            "primeira_compra",
            "primeiro_lance",
            "primeiro_cupom",
            "primeiro_pedido_pagamento",
            "primeiro_pagamento_concluido",
            "primeira_transferencia_para_o_jogo",
            "primeira_transferencia_para_jogador",
            "primeira_retirada_item",
            "primeira_insercao_item",
            "primeira_troca_itens",
            "primeiro_vencedor_leilao",
            "primeiro_bonus"
        ],
        
        "📦 CONQUISTAS DE INVENTÁRIO": [
            "colecionador_itens",
            "mestre_inventario",
            "trocador_incansavel"
        ],
        
        "💰 CONQUISTAS DE CARTEIRA E TRANSFERÊNCIAS": [
            "gerenciador_economico",
            "benfeitor_comunitario",
            "100_transacoes",
            "250_transacoes", 
            "500_transacoes"
        ],
        
        "🎁 CONQUISTAS DE BÔNUS": [
            "bonus_diario_7dias",
            "bonus_diario_30dias",
            "bonus_mestre",
            "bonus_expert"
        ],
        
        "💎 CONQUISTAS DE PATROCÍNIO": [
            "patrocinador_ouro",
            "patrocinador_diamante"
        ],
        
        "🛒 CONQUISTAS DE LOJA": [
            "comprador_frequente",
            "comprador_vip"
        ],
        
        "🏛️ CONQUISTAS DE LEILÕES": [
            "10_leiloes",
            "leiloeiro_profissional",
            "leiloeiro_mestre",
            "50_lances",
            "lanceador_profissional",
            "lanceador_mestre",
            "vencedor_serie",
            "vencedor_mestre"
        ],
        
        "🎫 CONQUISTAS DE CUPONS": [
            "cupom_mestre",
            "cupom_expert"
        ],
        
        "🆘 CONQUISTAS DE SUPORTE": [
            "solicitante_frequente",
            "solicitante_expert",
            "resolvedor_problemas",
            "resolvedor_mestre"
        ],
        
        "👥 CONQUISTAS DE REDE SOCIAL": [
            "rede_social",
            "rede_social_mestre"
        ],
        
        "📈 CONQUISTAS DE NÍVEL": [
            "nivel_10",
            "nivel_25",
            "nivel_50",
            "nivel_75",
            "nivel_100"
        ],
        
        "⭐ CONQUISTAS DE EXPERIÊNCIA": [
            "1000_xp",
            "5000_xp",
            "10000_xp"
        ]
    }
    
    # Buscar todas as conquistas do banco
    todas_conquistas = {c.codigo: c for c in Conquista.objects.all()}
    total_conquistas = len(todas_conquistas)
    
    # Gerar conteúdo para cada categoria
    for categoria, codigos in categorias.items():
        # Cabeçalho da categoria
        story.append(create_category_header(categoria, len(codigos)))
        
        # Barra de progresso da categoria
        progresso_text = create_progress_bar(codigos, total_conquistas)
        story.append(Paragraph(f"<b>{progresso_text}</b>", achievement_style))
        story.append(Spacer(1, 15))
        
        # Conquistas da categoria
        for codigo in codigos:
            if codigo in todas_conquistas:
                conquista = todas_conquistas[codigo]
                
                # Criar caixa estilizada para a conquista
                categoria_icon = categoria.split()[0]  # Pega o ícone da categoria
                achievement_box = create_achievement_box(conquista, instrucoes_conquistas.get(codigo, "Instrução não disponível"), categoria_icon)
                story.append(achievement_box)
                story.append(Spacer(1, 10))
        
        story.append(Spacer(1, 20))
    
    # Adicionar página de estratégias com design melhorado
    story.append(PageBreak())
    story.append(Paragraph("🎯 ESTRATÉGIAS AVANÇADAS PARA MAXIMIZAR CONQUISTAS", subtitle_style))
    
    estrategias = [
        "<b>1. 🎮 Configure seu perfil completamente:</b><br/>• Verifique email, configure 2FA, adicione endereço e avatar<br/>• Isso desbloqueia várias conquistas de primeira vez de forma rápida",
        
        "<b>2. 📅 Seja ativo diariamente:</b><br/>• Receba bônus diários para acumular XP e conquistas de bônus<br/>• Participe regularmente para manter progresso constante",
        
        "<b>3. 🏛️ Participe do sistema de leilões:</b><br/>• Crie leilões para vender itens e ganhar moedas<br/>• Lance em leilões de outros jogadores para encontrar itens raros<br/>• Tente vencer leilões para conquistas específicas de vencedor",
        
        "<b>4. 🛒 Use a loja regularmente:</b><br/>• Faça compras para desbloquear conquistas de comprador<br/>• Aplique cupons promocionais quando disponíveis para economizar<br/>• Mantenha-se atento a promoções especiais",
        
        "<b>5. 👥 Construa sua rede social:</b><br/>• Adicione amigos e aceite solicitações regularmente<br/>• Mantenha uma rede ativa de jogadores para trocas<br/>• Participe de grupos e comunidades",
        
        "<b>6. 💰 Gerencie sua carteira estrategicamente:</b><br/>• Faça transferências para o jogo e outros jogadores<br/>• Realize transações regularmente para acumular conquistas<br/>• Mantenha um fluxo constante de moedas",
        
        "<b>7. 💎 Contribua com o servidor:</b><br/>• Faça pagamentos para se tornar patrocinador<br/>• Apoie o desenvolvimento do servidor e receba benefícios<br/>• Alcance status de patrocinador ouro e diamante",
        
        "<b>8. 📦 Gerencie seu inventário eficientemente:</b><br/>• Colecione itens do jogo de forma organizada<br/>• Faça trocas entre personagens regularmente<br/>• Mantenha um inventário diversificado",
        
        "<b>9. 🆘 Peça ajuda quando necessário:</b><br/>• Abra solicitações de suporte quando tiver problemas<br/>• Isso pode gerar conquistas de suporte e resolver questões<br/>• Mantenha um histórico de solicitações resolvidas",
        
        "<b>10. 📢 Mantenha-se informado:</b><br/>• Fique atento a novos cupons e promoções<br/>• Participe de eventos especiais e temporários<br/>• Siga as atualizações do sistema"
    ]
    
    for estrategia in estrategias:
        story.append(Paragraph(estrategia, strategy_style))
        story.append(Spacer(1, 8))
    
    # Adicionar página de recompensas com design melhorado
    story.append(PageBreak())
    story.append(Paragraph("🎁 SISTEMA DE RECOMPENSAS DETALHADO", subtitle_style))
    
    recompensas_text = """
    <b>🏆 Como funcionam as recompensas:</b><br/><br/>
    
    <b>💎 Recompensas por Conquista:</b><br/>
    • Cada conquista pode dar itens especiais do jogo diretamente para seu inventário<br/>
    • Itens raros e exclusivos que não podem ser obtidos de outra forma<br/>
    • Recompensas variam de acordo com a dificuldade da conquista<br/><br/>
    
    <b>🌟 Recompensas por Múltiplas Conquistas:</b><br/>
    • Desbloquear muitas conquistas pode dar recompensas extras<br/>
    • Bônus especiais para completar categorias inteiras<br/>
    • Recompensas progressivas conforme você avança<br/><br/>
    
    <b>📈 Recompensas por Nível:</b><br/>
    • Subir de nível também pode dar itens especiais<br/>
    • Recompensas maiores em níveis importantes (10, 25, 50, 75, 100)<br/>
    • Benefícios exclusivos para jogadores de alto nível<br/><br/>
    
    <b>⚡ Sistema Automático:</b><br/>
    • As recompensas são enviadas automaticamente para seu inventário<br/>
    • Notificações instantâneas quando conquistas são desbloqueadas<br/>
    • Sistema confiável e sem necessidade de reivindicação manual<br/><br/>
    
    <b>🎯 Recompensas Únicas:</b><br/>
    • Algumas conquistas dão recompensas exclusivas que não podem ser obtidas de outra forma<br/>
    • Itens colecionáveis especiais para mostrar seu progresso<br/>
    • Títulos e badges exclusivos para seu perfil<br/><br/>
    
    <b>💡 Dica Pro:</b> Mantenha-se ativo e participe de todas as funcionalidades do sistema para maximizar suas recompensas e construir uma coleção impressionante!
    """
    
    story.append(Paragraph(recompensas_text, desc_style))
    
    # Adicionar página de estatísticas com design melhorado
    story.append(PageBreak())
    story.append(Paragraph("📊 ESTATÍSTICAS COMPLETAS DO SISTEMA", subtitle_style))
    
    categorias_count = len(categorias)
    conquistas_primeira_vez = len(categorias['🎮 CONQUISTAS DE PRIMEIRA VEZ'])
    conquistas_progresso = len(categorias['📈 CONQUISTAS DE NÍVEL']) + len(categorias['⭐ CONQUISTAS DE EXPERIÊNCIA'])
    conquistas_atividade = len(categorias['🏛️ CONQUISTAS DE LEILÕES']) + len(categorias['🛒 CONQUISTAS DE LOJA'])
    
    stats_text = f"""
    <b>📈 Resumo completo do sistema de conquistas:</b><br/><br/>
    
    <b>🎯 Estatísticas Gerais:</b><br/>
    • <b>Total de Conquistas:</b> {total_conquistas} conquistas disponíveis<br/>
    • <b>Categorias:</b> {categorias_count} categorias diferentes<br/>
    • <b>Conquistas de Primeira Vez:</b> {conquistas_primeira_vez} conquistas (mais fáceis)<br/>
    • <b>Conquistas de Progresso:</b> {conquistas_progresso} conquistas (nível e XP)<br/>
    • <b>Conquistas de Atividade:</b> {conquistas_atividade} conquistas (leilões e loja)<br/><br/>
    
    <b>📊 Distribuição por Categoria:</b><br/>
    • 🎮 Primeira Vez: {conquistas_primeira_vez} conquistas<br/>
    • 📦 Inventário: {len(categorias['📦 CONQUISTAS DE INVENTÁRIO'])} conquistas<br/>
    • 💰 Carteira: {len(categorias['💰 CONQUISTAS DE CARTEIRA E TRANSFERÊNCIAS'])} conquistas<br/>
    • 🎁 Bônus: {len(categorias['🎁 CONQUISTAS DE BÔNUS'])} conquistas<br/>
    • 💎 Patrocínio: {len(categorias['💎 CONQUISTAS DE PATROCÍNIO'])} conquistas<br/>
    • 🛒 Loja: {len(categorias['🛒 CONQUISTAS DE LOJA'])} conquistas<br/>
    • 🏛️ Leilões: {len(categorias['🏛️ CONQUISTAS DE LEILÕES'])} conquistas<br/>
    • 🎫 Cupons: {len(categorias['🎫 CONQUISTAS DE CUPONS'])} conquistas<br/>
    • 🆘 Suporte: {len(categorias['🆘 CONQUISTAS DE SUPORTE'])} conquistas<br/>
    • 👥 Rede Social: {len(categorias['👥 CONQUISTAS DE REDE SOCIAL'])} conquistas<br/>
    • 📈 Nível: {len(categorias['📈 CONQUISTAS DE NÍVEL'])} conquistas<br/>
    • ⭐ Experiência: {len(categorias['⭐ CONQUISTAS DE EXPERIÊNCIA'])} conquistas<br/><br/>
    
    <b>🎯 Progresso Recomendado:</b><br/>
    1. 🎮 Comece pelas conquistas de primeira vez (mais fáceis e rápidas)<br/>
    2. 📅 Foque em atividades diárias para acumular XP constantemente<br/>
    3. 🏛️ Participe de leilões e use a loja regularmente<br/>
    4. 👥 Construa sua rede social e mantenha conexões ativas<br/>
    5. 💎 Contribua com o servidor para se tornar patrocinador<br/>
    6. 📦 Gerencie inventário e carteira de forma estratégica<br/>
    7. 🆘 Use o suporte quando necessário<br/>
    8. 🎫 Aproveite cupons e promoções<br/>
    9. 📈 Mantenha foco no progresso de nível<br/>
    10. ⭐ Acumule experiência através de todas as atividades<br/><br/>
    
    <b>💡 Dica Final:</b> O sistema de conquistas é projetado para recompensar tanto jogadores casuais quanto hardcore. 
    Cada atividade que você realiza no sistema pode contribuir para múltiplas conquistas simultaneamente!
    """
    
    story.append(Paragraph(stats_text, stats_style))
    
    # Adicionar página final com informações de contato
    story.append(PageBreak())
    story.append(Paragraph("📞 INFORMAÇÕES DE CONTATO E SUPORTE", subtitle_style))
    
    contato_text = """
    <b>🆘 Precisa de ajuda?</b><br/><br/>
    
    <b>📧 Suporte Técnico:</b><br/>
    • Abra uma solicitação de suporte através do sistema<br/>
    • Nossa equipe responderá o mais rápido possível<br/>
    • Inclua detalhes específicos sobre seu problema<br/><br/>
    
    <b>📚 Recursos Adicionais:</b><br/>
    • Este guia é atualizado regularmente com novas conquistas<br/>
    • Fique atento às atualizações do sistema<br/>
    • Participe da comunidade para dicas e truques<br/><br/>
    
    <b>🎯 Objetivo do Sistema:</b><br/>
    • Recompensar jogadores ativos e dedicados<br/>
    • Criar uma experiência envolvente e progressiva<br/>
    • Fomentar a interação entre membros da comunidade<br/>
    • Manter o engajamento através de metas claras<br/><br/>
    
    <b>🌟 Boa sorte em sua jornada de conquistas!</b><br/>
    Que cada conquista seja um passo em direção ao sucesso no jogo!
    """
    
    story.append(Paragraph(contato_text, desc_style))
    
    # Gerar o PDF
    doc.build(story)
    print("✅ PDF detalhado gerado com sucesso: Guia_Conquistas_Detalhado.pdf")
    print("📊 Estatísticas do PDF:")
    print(f"   • Total de conquistas: {total_conquistas}")
    print(f"   • Categorias: {categorias_count}")
    print(f"   • Páginas estimadas: {len(story) // 15 + 1}")

if __name__ == "__main__":
    try:
        gerar_pdf_conquistas_detalhado()
    except Exception as e:
        print(f"❌ Erro ao gerar PDF detalhado: {e}")
        sys.exit(1) 