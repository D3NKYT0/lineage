#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
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

def create_header_footer(canvas, doc):
    """Cria cabeçalho e rodapé personalizados"""
    canvas.saveState()
    
    # Cabeçalho
    canvas.setFillColor(colors.darkblue)
    canvas.setFont("Helvetica-Bold", 12)
    canvas.drawString(72, A4[1] - 50, "📱 PDL SOCIAL - TUTORIAL COMPLETO")
    
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

def create_feature_box(titulo, descricao, instrucoes, categoria_icon):
    """Cria uma caixa estilizada para cada funcionalidade"""
    # Quebrar texto longo em múltiplas linhas
    def wrap_text(text, max_width=60):
        """Quebra texto em linhas de no máximo max_width caracteres"""
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            if len(current_line + " " + word) <= max_width:
                current_line += " " + word if current_line else word
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return lines
    
    # Quebrar textos longos
    titulo_lines = wrap_text(titulo, 45)
    descricao_lines = wrap_text(descricao, 50)
    instrucoes_lines = wrap_text(instrucoes, 50)
    
    # Criar linhas da tabela
    data = []
    
    # Título
    for line in titulo_lines:
        data.append([f"{categoria_icon} {line}"])
    
    # Descrição
    for line in descricao_lines:
        data.append([f"📝 {line}"])
    
    # Instruções
    for line in instrucoes_lines:
        data.append([f"🎯 {line}"])
    
    table = Table(data, colWidths=[350])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.lightblue, colors.white]),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('WORDWRAP', (0, 0), (-1, -1), True),  # Força quebra de palavras
    ]))
    
    return table

def create_section_header(secao_nome, total_funcionalidades):
    """Cria cabeçalho estilizado para seção"""
    data = [[f"{secao_nome}"]]
    
    table = Table(data, colWidths=[350])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 15),
        ('TOPPADDING', (0, 0), (-1, 0), 15),
        ('GRID', (0, 0), (-1, -1), 1, colors.darkgreen),
        ('WORDWRAP', (0, 0), (-1, -1), True),  # Força quebra de palavras
    ]))
    
    return table

def gerar_pdf_tutorial_social():
    """Gera um PDF tutorial detalhado da rede social PDL Social"""
    
    # Configurar o documento com template personalizado
    doc = SimpleDocTemplate(
        "Tutorial_PDL_Social_Completo.pdf",
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
    
    # Estilo para título principal
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
    
    # Estilo para subtítulos
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
    
    # Estilo para descrições
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
        borderPadding=10,
        wordWrap='CJK'  # Força quebra de palavras
    )
    
    # Estilo para funcionalidades
    feature_style = ParagraphStyle(
        'Feature',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=5,
        spaceBefore=5,
        leftIndent=0,
        fontName='Helvetica',
        wordWrap='CJK'  # Força quebra de palavras
    )
    
    # Estilo para instruções
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
        borderPadding=5,
        wordWrap='CJK'  # Força quebra de palavras
    )
    
    # Estilo para dicas
    tip_style = ParagraphStyle(
        'Tip',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=12,
        spaceBefore=8,
        leftIndent=20,
        fontName='Helvetica',
        backColor=colors.lightgreen,
        borderWidth=1,
        borderColor=colors.green,
        borderPadding=8,
        wordWrap='CJK'  # Força quebra de palavras
    )
    
    # Estilo para avisos
    warning_style = ParagraphStyle(
        'Warning',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=8,
        spaceBefore=8,
        leftIndent=20,
        fontName='Helvetica',
        backColor=colors.lightcyan,
        borderWidth=1,
        borderColor=colors.cyan,
        borderPadding=8,
        wordWrap='CJK'  # Força quebra de palavras
    )
    
    # Conteúdo do PDF
    story = []
    
    # Título principal
    story.append(Paragraph("📱 TUTORIAL COMPLETO - PDL SOCIAL", title_style))
    story.append(Spacer(1, 30))
    
    # Introdução
    intro_text = """
    <b>Bem-vindo ao PDL Social!</b><br/><br/>
    
    Este tutorial completo foi criado especialmente para usuários que estão começando a usar redes sociais 
    ou que querem aproveitar ao máximo todas as funcionalidades disponíveis na PDL Social. 
    Aqui você encontrará explicações detalhadas de cada recurso, passo a passo de como usar, 
    dicas importantes e melhores práticas para uma experiência incrível!<br/><br/>
    
    <b>O que é a PDL Social?</b><br/>
    • Uma rede social completa integrada ao sistema PDL<br/>
    • Conecte-se com outros jogadores e membros da comunidade<br/>
    • Compartilhe momentos, conquistas e experiências<br/>
    • Interaja através de curtidas, comentários e reações<br/>
    • Mantenha-se informado sobre novidades e eventos<br/><br/>
    
    <b>Por que usar a PDL Social?</b><br/>
    • <b>Comunidade:</b> Conecte-se com jogadores que compartilham seus interesses<br/>
    • <b>Informação:</b> Fique por dentro das últimas novidades do servidor<br/>
    • <b>Diversão:</b> Compartilhe suas conquistas e momentos especiais<br/>
    • <b>Suporte:</b> Peça ajuda e ajude outros membros da comunidade<br/>
    • <b>Networking:</b> Construa amizades duradouras com outros jogadores
    """
    story.append(Paragraph(intro_text, desc_style))
    story.append(Spacer(1, 30))
    
    # Dicionário com funcionalidades e instruções
    funcionalidades = {
        # SEÇÃO 1: CONFIGURAÇÃO INICIAL
        "📋 CONFIGURAÇÃO INICIAL E PERFIL": {
            "criar_perfil": {
                "titulo": "Criar seu Perfil Social",
                "descricao": "Configure seu perfil pessoal na rede social",
                "instrucoes": "Acesse 'Editar Perfil' no menu e preencha suas informações pessoais, adicione uma foto de perfil e uma imagem de capa"
            },
            "configurar_privacidade": {
                "titulo": "Configurar Privacidade",
                "descricao": "Defina quem pode ver seus posts e informações",
                "instrucoes": "No perfil, configure se quer um perfil público ou privado, e escolha quais informações mostrar"
            },
            "adicionar_bio": {
                "titulo": "Adicionar Biografia",
                "descricao": "Escreva uma breve descrição sobre você",
                "instrucoes": "Na seção de editar perfil, adicione uma biografia interessante que conte um pouco sobre você"
            },
            "configurar_avatar": {
                "titulo": "Configurar Avatar",
                "descricao": "Adicione uma foto de perfil personalizada",
                "instrucoes": "Faça upload de uma imagem (máx. 5MB) que será redimensionada automaticamente para 400x400px"
            },
            "adicionar_capa": {
                "titulo": "Adicionar Imagem de Capa",
                "descricao": "Personalize seu perfil com uma imagem de capa",
                "instrucoes": "Adicione uma imagem de capa (máx. 10MB, recomendado: 1200x400px) para deixar seu perfil mais atrativo"
            }
        },
        
        # SEÇÃO 2: NAVEGAÇÃO BÁSICA
        "🏠 NAVEGAÇÃO BÁSICA": {
            "acessar_feed": {
                "titulo": "Acessar o Feed Principal",
                "descricao": "Veja posts de pessoas que você segue e posts públicos",
                "instrucoes": "Clique em 'Feed' no menu principal para ver as publicações mais recentes"
            },
            "navegar_perfil": {
                "titulo": "Navegar pelo seu Perfil",
                "descricao": "Acesse e visualize seu perfil pessoal",
                "instrucoes": "Clique em seu nome de usuário ou 'Meu Perfil' para ver suas informações e posts"
            },
            "ver_meus_posts": {
                "titulo": "Ver Meus Posts",
                "descricao": "Visualize todas as suas publicações",
                "instrucoes": "Acesse 'Meus Posts' no menu para ver todas as suas publicações em ordem cronológica"
            },
            "usar_busca": {
                "titulo": "Usar a Busca",
                "descricao": "Encontre usuários, posts e hashtags",
                "instrucoes": "Use a barra de busca para encontrar usuários específicos, posts com palavras-chave ou hashtags"
            }
        },
        
        # SEÇÃO 3: CRIAR E GERENCIAR POSTS
        "✍️ CRIAR E GERENCIAR POSTS": {
            "criar_post": {
                "titulo": "Criar um Post",
                "descricao": "Publique conteúdo na rede social",
                "instrucoes": "Clique em 'Criar Post' e escreva seu conteúdo. Você pode adicionar texto, imagens, vídeos e links"
            },
            "adicionar_imagem": {
                "titulo": "Adicionar Imagem ao Post",
                "descricao": "Inclua imagens nas suas publicações",
                "instrucoes": "Ao criar um post, clique em 'Adicionar Imagem' e selecione uma foto (máx. 10MB, 1920x1080px)"
            },
            "adicionar_video": {
                "titulo": "Adicionar Vídeo ao Post",
                "descricao": "Inclua vídeos nas suas publicações",
                "instrucoes": "Selecione 'Adicionar Vídeo' e faça upload de um vídeo (máx. 100MB, 5min, formatos: MP4/MOV/AVI/WEBM)"
            },
            "adicionar_link": {
                "titulo": "Adicionar Link ao Post",
                "descricao": "Compartilhe links interessantes",
                "instrucoes": "Cole um URL no campo de link. O sistema automaticamente mostrará título, descrição e imagem do link"
            },
            "usar_hashtags": {
                "titulo": "Usar Hashtags",
                "descricao": "Organize e categorize seus posts",
                "instrucoes": "Adicione #hashtags no seu texto para categorizar o post e torná-lo mais fácil de encontrar"
            },
            "editar_post": {
                "titulo": "Editar um Post",
                "descricao": "Modifique suas publicações após publicar",
                "instrucoes": "Clique nos três pontos do seu post e selecione 'Editar' para modificar o conteúdo"
            },
            "deletar_post": {
                "titulo": "Deletar um Post",
                "descricao": "Remova publicações que não deseja manter",
                "instrucoes": "Nos três pontos do post, selecione 'Deletar' e confirme a ação (não pode ser desfeita)"
            },
            "fixar_post": {
                "titulo": "Fixar um Post",
                "descricao": "Destaque um post importante no seu perfil",
                "instrucoes": "Use a opção 'Fixar' para manter um post no topo do seu perfil por tempo indeterminado"
            }
        },
        
        # SEÇÃO 4: INTERAÇÕES E ENGAGEMENT
        "👍 INTERAÇÕES E ENGAGEMENT": {
            "curtir_post": {
                "titulo": "Curtir um Post",
                "descricao": "Demonstre que gostou de uma publicação",
                "instrucoes": "Clique no botão de curtir (👍) abaixo do post para mostrar que gostou do conteúdo"
            },
            "usar_reacoes": {
                "titulo": "Usar Reações",
                "descricao": "Expresse diferentes emoções nos posts",
                "instrucoes": "Clique e segure o botão de curtir para ver opções: 👍 Curtir, ❤️ Amar, 😂 Haha, 😮 Uau, 😢 Triste, 😠 Bravo"
            },
            "comentar_post": {
                "titulo": "Comentar em um Post",
                "descricao": "Deixe sua opinião ou pergunta",
                "instrucoes": "Clique em 'Comentar' e escreva sua mensagem. Você pode adicionar imagens nos comentários também"
            },
            "responder_comentario": {
                "titulo": "Responder a um Comentário",
                "descricao": "Interaja com outros comentários",
                "instrucoes": "Clique em 'Responder' em um comentário para criar uma conversa em thread"
            },
            "curtir_comentario": {
                "titulo": "Curtir um Comentário",
                "descricao": "Demonstre que concorda com um comentário",
                "instrucoes": "Clique no botão de curtir abaixo do comentário para mostrar aprovação"
            },
            "compartilhar_post": {
                "titulo": "Compartilhar um Post",
                "descricao": "Republique conteúdo interessante",
                "instrucoes": "Clique em 'Compartilhar' e adicione um comentário opcional antes de republicar"
            }
        },
        
        # SEÇÃO 5: CONEXÕES E SEGUIDORES
        "👥 CONEXÕES E SEGUIDORES": {
            "seguir_usuario": {
                "titulo": "Seguir um Usuário",
                "descricao": "Acompanhe as publicações de outros usuários",
                "instrucoes": "Clique em 'Seguir' no perfil de um usuário para ver seus posts no seu feed"
            },
            "deixar_seguir": {
                "titulo": "Deixar de Seguir",
                "descricao": "Pare de acompanhar um usuário",
                "instrucoes": "Clique em 'Deixar de Seguir' no perfil para parar de ver os posts dessa pessoa"
            },
            "ver_seguidores": {
                "titulo": "Ver Meus Seguidores",
                "descricao": "Visualize quem te segue",
                "instrucoes": "No seu perfil, clique em 'Seguidores' para ver a lista de pessoas que te seguem"
            },
            "ver_seguindo": {
                "titulo": "Ver Quem Eu Sigo",
                "descricao": "Visualize quem você segue",
                "instrucoes": "No seu perfil, clique em 'Seguindo' para ver a lista de pessoas que você segue"
            },
            "configurar_notificacoes": {
                "titulo": "Configurar Notificações",
                "descricao": "Escolha quais notificações receber",
                "instrucoes": "Ao seguir alguém, você pode desativar notificações específicas nas configurações"
            }
        },
        
        # SEÇÃO 6: HASHTAGS E DESCOBERTA
        "🏷️ HASHTAGS E DESCOBERTA": {
            "criar_hashtag": {
                "titulo": "Criar uma Hashtag",
                "descricao": "Organize conteúdo com tags personalizadas",
                "instrucoes": "Escreva #sua_hashtag no seu post. Se for nova, ela será criada automaticamente"
            },
            "explorar_hashtags": {
                "titulo": "Explorar Hashtags",
                "descricao": "Descubra conteúdo por categorias",
                "instrucoes": "Clique em qualquer hashtag para ver todos os posts que a utilizam"
            },
            "ver_hashtags_populares": {
                "titulo": "Ver Hashtags Populares",
                "descricao": "Descubra as tags mais usadas",
                "instrucoes": "No feed, veja a seção de hashtags populares para descobrir tendências"
            },
            "seguir_hashtag": {
                "titulo": "Seguir uma Hashtag",
                "descricao": "Acompanhe posts de uma categoria específica",
                "instrucoes": "Ao clicar em uma hashtag, você pode salvá-la para acompanhar posts futuros"
            }
        },
        
        # SEÇÃO 7: PRIVACIDADE E SEGURANÇA
        "🔒 PRIVACIDADE E SEGURANÇA": {
            "configurar_perfil_privado": {
                "titulo": "Configurar Perfil Privado",
                "descricao": "Controle quem pode ver seus posts",
                "instrucoes": "Nas configurações do perfil, ative 'Perfil Privado' para que apenas seguidores aprovados vejam seus posts"
            },
            "gerenciar_seguidores": {
                "titulo": "Gerenciar Seguidores",
                "descricao": "Aprove ou rejeite solicitações de seguidores",
                "instrucoes": "Com perfil privado, você pode aprovar ou rejeitar quem quer te seguir"
            },
            "denunciar_conteudo": {
                "titulo": "Denunciar Conteúdo Inapropriado",
                "descricao": "Ajude a manter a comunidade segura",
                "instrucoes": "Use o botão de denúncia (⚠️) em posts ou comentários que violem as regras"
            },
            "bloquear_usuario": {
                "titulo": "Bloquear um Usuário",
                "descricao": "Evite interações indesejadas",
                "instrucoes": "Nas configurações do perfil de um usuário, você pode bloquear para não ver mais o conteúdo dele"
            },
            "configurar_visibilidade": {
                "titulo": "Configurar Visibilidade de Informações",
                "descricao": "Controle quais dados pessoais são visíveis",
                "instrucoes": "Configure se quer mostrar email, telefone e outras informações pessoais no perfil"
            }
        },
        
        # SEÇÃO 8: FUNÇÕES AVANÇADAS
        "⚙️ FUNÇÕES AVANÇADAS": {
            "usar_busca_avancada": {
                "titulo": "Usar Busca Avançada",
                "descricao": "Encontre conteúdo específico com filtros",
                "instrucoes": "Use a busca com filtros por data, tipo de conteúdo, usuário ou hashtag"
            },
            "salvar_posts": {
                "titulo": "Salvar Posts Favoritos",
                "descricao": "Guarde posts para ver depois",
                "instrucoes": "Use o botão de salvar (🔖) para guardar posts interessantes em uma lista pessoal"
            },
            "ver_estatisticas": {
                "titulo": "Ver Estatísticas do Perfil",
                "descricao": "Acompanhe seu engajamento na rede",
                "instrucoes": "No seu perfil, veja estatísticas como total de posts, curtidas recebidas e seguidores"
            },
            "exportar_dados": {
                "titulo": "Exportar Dados do Perfil",
                "descricao": "Faça backup das suas informações",
                "instrucoes": "Nas configurações, você pode solicitar uma cópia de todos os seus dados"
            },
            "configurar_notificacoes_avancadas": {
                "titulo": "Configurar Notificações Avançadas",
                "descricao": "Personalize alertas e lembretes",
                "instrucoes": "Configure notificações por email, push e web para diferentes tipos de atividade"
            }
        }
    }
    
    # Gerar conteúdo para cada seção
    for secao, funcionalidades_secao in funcionalidades.items():
        # Cabeçalho da seção
        story.append(create_section_header(secao, len(funcionalidades_secao)))
        story.append(Spacer(1, 15))
        
        # Funcionalidades da seção
        for codigo, funcionalidade in funcionalidades_secao.items():
            # Criar caixa estilizada para a funcionalidade
            categoria_icon = secao.split()[0]  # Pega o ícone da seção
            feature_box = create_feature_box(
                funcionalidade["titulo"], 
                funcionalidade["descricao"], 
                funcionalidade["instrucoes"], 
                categoria_icon
            )
            story.append(feature_box)
            story.append(Spacer(1, 10))
        
        story.append(Spacer(1, 20))
    
    # Adicionar página de dicas e melhores práticas
    story.append(PageBreak())
    story.append(Paragraph("💡 DICAS E MELHORES PRÁTICAS", subtitle_style))
    
    dicas = [
        "<b>1. 📝 Seja autêntico:</b><br/>• Compartilhe conteúdo real e pessoal<br/>• Evite posts genéricos ou copiados<br/>• Mostre sua personalidade única",
        
        "<b>2. 🎯 Use hashtags estrategicamente:</b><br/>• Use 3-5 hashtags relevantes por post<br/>• Misture hashtags populares e específicas<br/>• Crie hashtags únicas para sua comunidade",
        
        "<b>3. 📸 Qualidade das imagens:</b><br/>• Use fotos claras e bem iluminadas<br/>• Mantenha proporções adequadas<br/>• Evite imagens borradas ou de baixa qualidade",
        
        "<b>4. ⏰ Frequência de posts:</b><br/>• Mantenha uma frequência consistente<br/>• Não poste em excesso (evite spam)<br/>• Escolha horários em que sua audiência está ativa",
        
        "<b>5. 💬 Interaja genuinamente:</b><br/>• Responda comentários de forma sincera<br/>• Faça perguntas para gerar conversas<br/>• Agradeça curtidas e comentários",
        
        "<b>6. 🔍 Conteúdo valioso:</b><br/>• Compartilhe dicas úteis sobre o jogo<br/>• Celebre conquistas e momentos especiais<br/>• Ajude outros jogadores com dúvidas",
        
        "<b>7. 🛡️ Respeite a comunidade:</b><br/>• Siga as regras da plataforma<br/>• Seja respeitoso com outros usuários<br/>• Denuncie conteúdo inapropriado",
        
        "<b>8. 📊 Analise seu engajamento:</b><br/>• Observe quais posts têm mais sucesso<br/>• Aprenda com o feedback da comunidade<br/>• Adapte seu conteúdo baseado nas reações",
        
        "<b>9. 🌟 Construa relacionamentos:</b><br/>• Siga usuários com interesses similares<br/>• Participe de conversas relevantes<br/>• Seja um membro ativo da comunidade",
        
        "<b>10. 🎮 Integre com o jogo:</b><br/>• Compartilhe conquistas do jogo<br/>• Poste sobre eventos e atualizações<br/>• Conecte-se com membros do seu clã/guilda"
    ]
    
    for dica in dicas:
        story.append(Paragraph(dica, tip_style))
        story.append(Spacer(1, 8))
    
    # Adicionar página de segurança e privacidade
    story.append(PageBreak())
    story.append(Paragraph("🛡️ SEGURANÇA E PRIVACIDADE", subtitle_style))
    
    seguranca_text = """
    <b>🔐 Protegendo sua Privacidade:</b><br/><br/>
    
    <b>📱 Informações Pessoais:</b><br/>
    • Nunca compartilhe senhas, emails ou dados bancários<br/>
    • Use um nome de usuário diferente do seu nome real<br/>
    • Configure cuidadosamente as opções de privacidade<br/><br/>
    
    <b>🌐 Configurações de Perfil:</b><br/>
    • Escolha se quer um perfil público ou privado<br/>
    • Decida quais informações pessoais mostrar<br/>
    • Controle quem pode te enviar mensagens<br/><br/>
    
    <b>⚠️ Conteúdo Sensível:</b><br/>
    • Evite postar informações muito pessoais<br/>
    • Não compartilhe localização em tempo real<br/>
    • Tenha cuidado com fotos que mostram sua casa/localização<br/><br/>
    
    <b>🚨 Denúncias e Moderação:</b><br/>
    • Denuncie conteúdo que viole as regras<br/>
    • Bloqueie usuários que te incomodam<br/>
    • Use as ferramentas de moderação disponíveis<br/><br/>
    
    <b>🔍 Verificação de Conta:</b><br/>
    • Mantenha seu email verificado<br/>
    • Use autenticação de dois fatores se disponível<br/>
    • Monitore atividades suspeitas na sua conta<br/><br/>
    
    <b>💡 Dicas de Segurança:</b><br/>
    • Use senhas fortes e únicas<br/>
    • Faça logout em dispositivos compartilhados<br/>
    • Mantenha seu navegador e apps atualizados<br/>
    • Desconfie de links suspeitos ou ofertas muito boas
    """
    
    story.append(Paragraph(seguranca_text, desc_style))
    
    # Adicionar página de solução de problemas
    story.append(PageBreak())
    story.append(Paragraph("🔧 SOLUÇÃO DE PROBLEMAS COMUNS", subtitle_style))
    
    problemas = [
        "<b>❓ Não consigo fazer login:</b><br/>• Verifique se o email e senha estão corretos<br/>• Tente recuperar sua senha se necessário<br/>• Limpe o cache do navegador",
        
        "<b>📱 Posts não aparecem no feed:</b><br/>• Verifique se o post foi publicado com sucesso<br/>• Confirme se não está em modo rascunho<br/>• Aguarde alguns minutos para sincronização",
        
        "<b>🖼️ Imagem não carrega:</b><br/>• Verifique o tamanho da imagem (máx. 10MB)<br/>• Use formatos suportados: JPG, PNG, GIF<br/>• Tente redimensionar a imagem",
        
        "<b>🎥 Vídeo não reproduz:</b><br/>• Verifique o formato (MP4, MOV, AVI, WEBM)<br/>• Confirme o tamanho (máx. 100MB)<br/>• Aguarde o processamento do vídeo",
        
        "<b>👥 Não consigo seguir usuários:</b><br/>• Verifique se o usuário não te bloqueou<br/>• Confirme se o perfil não é privado<br/>• Aguarde aprovação se for perfil privado",
        
        "<b>💬 Comentários não aparecem:</b><br/>• Verifique se o comentário foi enviado<br/>• Aguarde alguns segundos para atualização<br/>• Recarregue a página se necessário",
        
        "<b>🔍 Busca não funciona:</b><br/>• Verifique a ortografia das palavras-chave<br/>• Tente termos mais específicos<br/>• Use hashtags para encontrar conteúdo",
        
        "<b>📧 Não recebo notificações:</b><br/>• Verifique as configurações de notificação<br/>• Confirme se o email está verificado<br/>• Verifique a pasta de spam",
        
        "<b>🔄 Página não carrega:</b><br/>• Verifique sua conexão com a internet<br/>• Limpe o cache do navegador<br/>• Tente acessar em modo incógnito",
        
        "<b>📊 Estatísticas não atualizam:</b><br/>• Aguarde alguns minutos para sincronização<br/>• Recarregue a página<br/>• Verifique se as ações foram registradas"
    ]
    
    for problema in problemas:
        story.append(Paragraph(problema, warning_style))
        story.append(Spacer(1, 8))
    
    # Adicionar página final com recursos adicionais
    story.append(PageBreak())
    story.append(Paragraph("📚 RECURSOS ADICIONAIS E SUPORTE", subtitle_style))
    
    recursos_text = """
    <b>📖 Recursos de Aprendizado:</b><br/><br/>
    
    <b>🎯 Guias Específicos:</b><br/>
    • Tutorial de criação de posts atrativos<br/>
    • Guia de hashtags eficazes<br/>
    • Manual de configurações de privacidade<br/>
    • Dicas de engajamento da comunidade<br/><br/>
    
    <b>🆘 Suporte Técnico:</b><br/>
    • Sistema de tickets de suporte integrado<br/>
    • FAQ com perguntas frequentes<br/>
    • Chat de suporte em tempo real<br/>
    • Base de conhecimento completa<br/><br/>
    
    <b>👥 Comunidade:</b><br/>
    • Fórum de discussão da comunidade<br/>
    • Grupos temáticos por interesse<br/>
    • Eventos e encontros virtuais<br/>
    • Programa de embaixadores<br/><br/>
    
    <b>📢 Atualizações:</b><br/>
    • Blog com novidades e atualizações<br/>
    • Newsletter semanal de novidades<br/>
    • Canal de anúncios oficial<br/>
    • Roadmap de funcionalidades futuras<br/><br/>
    
    <b>🎮 Integração com o Jogo:</b><br/>
    • Compartilhamento automático de conquistas<br/>
    • Posts sobre eventos do servidor<br/>
    • Integração com sistema de clãs/guildas<br/>
    • Feed de atividades do jogo<br/><br/>
    
    <b>🌟 Próximos Passos:</b><br/>
    • Explore todas as funcionalidades gradualmente<br/>
    • Conecte-se com outros jogadores<br/>
    • Compartilhe suas experiências<br/>
    • Ajude a construir uma comunidade incrível!<br/><br/>
    
    <b>💡 Lembre-se:</b> A PDL Social é uma ferramenta poderosa para conectar-se com outros jogadores, 
    compartilhar experiências e fazer parte de uma comunidade incrível. Use-a com responsabilidade 
    e aproveite ao máximo todas as funcionalidades disponíveis!
    """
    
    story.append(Paragraph(recursos_text, desc_style))
    
    # Adicionar página de contato
    story.append(PageBreak())
    story.append(Paragraph("📞 INFORMAÇÕES DE CONTATO", subtitle_style))
    
    contato_text = """
    <b>🆘 Precisa de ajuda?</b><br/><br/>
    
    <b>📧 Suporte Técnico:</b><br/>
    • Abra uma solicitação de suporte através do sistema<br/>
    • Nossa equipe responderá o mais rápido possível<br/>
    • Inclua detalhes específicos sobre seu problema<br/><br/>
    
    <b>📚 Recursos de Ajuda:</b><br/>
    • Este tutorial é atualizado regularmente<br/>
    • Fique atento às novidades e atualizações<br/>
    • Participe da comunidade para dicas e truques<br/><br/>
    
    <b>🎯 Objetivo da PDL Social:</b><br/>
    • Conectar jogadores e criar uma comunidade ativa<br/>
    • Facilitar a comunicação e compartilhamento<br/>
    • Proporcionar uma experiência social rica e segura<br/>
    • Integrar a experiência social com o jogo<br/><br/>
    
    <b>🌟 Boa sorte em sua jornada social!</b><br/>
    Que cada post seja uma oportunidade de conectar-se com outros jogadores e fazer novos amigos!
    """
    
    story.append(Paragraph(contato_text, desc_style))
    
    # Gerar o PDF
    doc.build(story)
    print("✅ PDF tutorial da PDL Social gerado com sucesso: Tutorial_PDL_Social_Completo.pdf")
    print("📊 Estatísticas do PDF:")
    print(f"   • Total de funcionalidades: {sum(len(secao) for secao in funcionalidades.values())}")
    print(f"   • Seções: {len(funcionalidades)}")
    print(f"   • Páginas estimadas: {len(story) // 15 + 1}")

if __name__ == "__main__":
    try:
        gerar_pdf_tutorial_social()
    except Exception as e:
        print(f"❌ Erro ao gerar PDF tutorial: {e}")
        sys.exit(1)
