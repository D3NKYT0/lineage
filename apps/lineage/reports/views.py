import json

from django.shortcuts import render
from django.db.models import Sum, Count, Max, F
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from django.utils.timezone import now, timedelta

from apps.lineage.auction.models import Auction, Bid
from apps.lineage.inventory.models import InventoryLog
from apps.lineage.shop.models import ShopPurchase, ShopItem, ShopPackage, PromotionCode, Cart
from apps.main.home.models import User
from apps.main.social.models import Post, Comment, Like, Share, UserProfile, Follow, Hashtag, PostHashtag


@staff_member_required
def dashboard(request):
    """Dashboard principal dos relatórios"""
    return render(request, 'reports/dashboard.html')


@staff_member_required
def relatorio_movimentacoes_inventario(request):
    dias = 15
    data_inicio = now() - timedelta(days=dias)

    logs = InventoryLog.objects.filter(timestamp__gte=data_inicio)

    # Agrupamento por dia
    agrupado_por_dia = (
        logs.extra(select={'dia': "DATE(timestamp)"})
        .values('dia', 'acao')
        .annotate(total=Sum('quantity'))
        .order_by('dia')
    )

    # Coleta das datas únicas
    dias_labels = sorted(set(log['dia'] for log in agrupado_por_dia))
    dias_labels_str = [str(dia) for dia in dias_labels]

    acoes = ['RETIROU_DO_JOGO', 'INSERIU_NO_JOGO', 'TROCA_ENTRE_PERSONAGENS', 'RECEBEU_TROCA', 'BAG_PARA_INVENTARIO']
    dados_por_acao = {acao: [0] * len(dias_labels) for acao in acoes}

    for log in agrupado_por_dia:
        dia = log['dia']
        idx = dias_labels.index(dia)
        acao = log['acao']
        if acao in dados_por_acao:
            dados_por_acao[acao][idx] = int(log['total'])

    # Itens mais trocados
    itens_trocados = (
        logs.filter(acao='TROCA_ENTRE_PERSONAGENS')
        .values('item_name')
        .annotate(total_trocado=Sum('quantity'))
        .order_by('-total_trocado')[:5]
    )

    # Itens mais movimentados
    itens_movimentados = (
        logs.values('item_name')
        .annotate(total_movimentado=Sum('quantity'))
        .order_by('-total_movimentado')[:5]
    )

    # Usuários mais ativos
    usuarios_ativos = (
        logs.values('user__username')
        .annotate(total_acoes=Count('id'))
        .order_by('-total_acoes')[:5]
    )

    # Personagens mais ativos
    personagens_ativos = (
        logs.values('inventory__character_name')
        .annotate(total_acoes=Count('id'))
        .order_by('-total_acoes')[:5]
    )

    # Itens mais encantados
    itens_encantados = (
        logs.filter(enchant__gt=0)
        .values('item_name')
        .annotate(
            total_encantado=Sum('quantity'),
            max_enchant=Max('enchant'),
            avg_enchant=Sum(F('enchant') * F('quantity')) / Sum('quantity')
        )
        .order_by('-total_encantado')[:5]
    )

    # Estatísticas gerais
    total_logs = logs.count()
    total_itens_unicos = logs.values('item_name').distinct().count()
    total_usuarios_ativos = logs.values('user').distinct().count()
    total_personagens_ativos = logs.values('inventory__character_name').distinct().count()

    total_retirado = sum(dados_por_acao['RETIROU_DO_JOGO'])
    total_inserido = sum(dados_por_acao['INSERIU_NO_JOGO'])
    total_troca = sum(dados_por_acao['TROCA_ENTRE_PERSONAGENS'])
    total_recebido = sum(dados_por_acao['RECEBEU_TROCA'])
    total_bag_para_inventario = sum(dados_por_acao['BAG_PARA_INVENTARIO'])

    contexto = {
        'labels': json.dumps(dias_labels_str),
        'retirados': json.dumps(dados_por_acao['RETIROU_DO_JOGO']),
        'inseridos': json.dumps(dados_por_acao['INSERIU_NO_JOGO']),
        'trocados': json.dumps(dados_por_acao['TROCA_ENTRE_PERSONAGENS']),
        'recebidos': json.dumps(dados_por_acao['RECEBEU_TROCA']),
        'bag_para_inventario': json.dumps(dados_por_acao['BAG_PARA_INVENTARIO']),
        'itens_trocados': itens_trocados,
        'itens_movimentados': itens_movimentados,
        'usuarios_ativos': usuarios_ativos,
        'personagens_ativos': personagens_ativos,
        'itens_encantados': itens_encantados,
        'total_retirado': total_retirado,
        'total_inserido': total_inserido,
        'total_troca': total_troca,
        'total_recebido': total_recebido,
        'total_bag_para_inventario': total_bag_para_inventario,
        'total_logs': total_logs,
        'total_itens_unicos': total_itens_unicos,
        'total_usuarios_ativos': total_usuarios_ativos,
        'total_personagens_ativos': total_personagens_ativos,
        'periodo_dias': dias,
    }

    return render(request, 'reports/relatorio_movimentacoes_inventario.html', contexto)


@staff_member_required
def relatorio_leiloes(request):
    # Leilões Ativos
    leiloes_ativos = Auction.objects.filter(end_time__gt=now(), status='pending').order_by('-end_time')

    # Histórico de Lances
    lances = Bid.objects.select_related('auction', 'bidder').order_by('-created_at')

    # Status dos Leilões
    leiloes_pendentes = Auction.objects.filter(status='pending').count()
    leiloes_fechados = Auction.objects.filter(status='finished').count()
    leiloes_expirados = Auction.objects.filter(status='expired').count()
    leiloes_cancelados = Auction.objects.filter(status='cancelled').count()

    # Leilões mais Populares (baseado no número de lances)
    leiloes_populares = Auction.objects.annotate(num_lances=Count('bids')).order_by('-num_lances')[:5]

    # Dados para gráficos
    status_labels = ['Pendentes', 'Finalizados', 'Expirados', 'Cancelados']
    status_values = [leiloes_pendentes, leiloes_fechados, leiloes_expirados, leiloes_cancelados]

    # Leilões mais populares - Top 5 com o número de lances
    leiloes_populares_names = [leilao.item_name for leilao in leiloes_populares]
    leiloes_populares_lances = [leilao.num_lances for leilao in leiloes_populares]

    contexto = {
        'leiloes_ativos': leiloes_ativos,
        'lances': lances,
        'leiloes_pendentes': leiloes_pendentes,
        'leiloes_fechados': leiloes_fechados,
        'leiloes_expirados': leiloes_expirados,
        'leiloes_cancelados': leiloes_cancelados,
        'leiloes_populares': leiloes_populares,
        'status_labels': status_labels,
        'status_values': status_values,
        'leiloes_populares_names': leiloes_populares_names,
        'leiloes_populares_lances': leiloes_populares_lances,
    }

    return render(request, 'reports/relatorio_leiloes.html', contexto)


@staff_member_required
def relatorio_compras(request):
    # Total de Compras
    total_compras = ShopPurchase.objects.count()
    total_pago = ShopPurchase.objects.aggregate(Sum('total_pago'))['total_pago__sum'] or 0

    # Carrinhos Abandonados
    carrinhos_abandonados = Cart.objects.filter(
        user__isnull=False
    ).exclude(
        user__in=ShopPurchase.objects.values('user')
    ).count()

    # Itens Mais Vendidos - Utilizando prefetch_related para otimizar a consulta
    itens_mais_vendidos = ShopItem.objects.annotate(
        quantidade_vendida=Sum('cartitem__quantidade')
    ).order_by('-quantidade_vendida')[:5]

    # Pacotes Populares
    pacotes_populares = ShopPackage.objects.annotate(
        quantidade_vendida=Sum('cartpackage__quantidade')
    ).order_by('-quantidade_vendida')[:5]

    # Promoções Utilizadas
    promocoes_utilizadas = PromotionCode.objects.annotate(
        quantidade_utilizada=Count('shoppurchase')
    ).order_by('-quantidade_utilizada')[:5]

    # Receita por Período (Última Semana)
    data_inicio = timezone.now() - timezone.timedelta(weeks=1)
    receita_periodo = ShopPurchase.objects.filter(
        data_compra__gte=data_inicio
    ).aggregate(Sum('total_pago'))['total_pago__sum'] or 0

    # Prepare os dados para o template
    contexto = {
        'total_compras': total_compras,
        'total_pago': total_pago,
        'carrinhos_abandonados': carrinhos_abandonados,
        'itens_mais_vendidos': [{'nome': item.nome, 'quantidade_vendida': item.quantidade_vendida or 0} for item in itens_mais_vendidos],
        'pacotes_populares': [{'nome': pacote.nome, 'quantidade_vendida': pacote.quantidade_vendida or 0} for pacote in pacotes_populares],
        'promocoes_utilizadas': [{'codigo': promocao.codigo, 'quantidade_utilizada': promocao.quantidade_utilizada} for promocao in promocoes_utilizadas],
        'receita_periodo': receita_periodo,
    }

    return render(request, 'reports/relatorio_compras.html', contexto)


@staff_member_required
def relatorio_rede_social(request):
    """Relatório completo da rede social"""
    
    # Estatísticas gerais
    total_posts = Post.objects.count()
    total_comments = Comment.objects.count()
    total_likes = Like.objects.count()
    total_shares = Share.objects.count()
    total_users = UserProfile.objects.count()
    total_follows = Follow.objects.count()
    total_hashtags = Hashtag.objects.count()
    
    # Posts por período (últimos 30 dias)
    data_inicio = now() - timedelta(days=30)
    posts_30_dias = Post.objects.filter(created_at__gte=data_inicio).count()
    posts_por_dia = (
        Post.objects.filter(created_at__gte=data_inicio)
        .extra(select={'dia': "DATE(created_at)"})
        .values('dia')
        .annotate(total=Count('id'))
        .order_by('dia')
    )
    
    # Usuários mais ativos
    usuarios_mais_ativos = (
        Post.objects.values('author__username')
        .annotate(
            total_posts=Count('id'),
            total_likes_received=Sum('likes_count'),
            total_comments_received=Sum('comments_count')
        )
        .order_by('-total_posts')[:10]
    )
    
    # Posts mais populares
    posts_mais_populares = (
        Post.objects.select_related('author')
        .annotate(
            total_engagement=F('likes_count') + F('comments_count') + F('shares_count')
        )
        .order_by('-total_engagement')[:10]
    )
    
    # Hashtags mais populares
    hashtags_populares = (
        PostHashtag.objects.values('hashtag__name')
        .annotate(
            total_posts=Count('post'),
            total_likes=Sum('post__likes_count'),
            total_comments=Sum('post__comments_count')
        )
        .order_by('-total_posts')[:10]
    )
    
    # Estatísticas de engajamento
    posts_com_imagem = Post.objects.filter(image__isnull=False).count()
    posts_com_video = Post.objects.filter(video__isnull=False).count()
    posts_com_link = Post.objects.filter(link__isnull=False).count()
    posts_fixados = Post.objects.filter(is_pinned=True).count()
    
    # Reações por tipo
    reacoes_por_tipo = (
        Like.objects.values('reaction_type')
        .annotate(total=Count('id'))
        .order_by('-total')
    )
    
    # Comentários mais curtidos
    comentarios_populares = (
        Comment.objects.select_related('post', 'author')
        .order_by('-likes_count')[:10]
    )
    
    # Usuários com mais seguidores - usando as relações corretas do modelo Follow
    usuarios_influentes = []
    
    # Buscar usuários com mais seguidores usando uma query otimizada
    users_with_followers = (
        User.objects.annotate(
            followers_count=Count('followers'),
            following_count=Count('following'),
            posts_count=Count('social_posts')
        )
        .filter(followers_count__gt=0)
        .order_by('-followers_count')[:10]
    )
    
    for user in users_with_followers:
        try:
            profile = user.social_profile
        except UserProfile.DoesNotExist:
            continue
            
        usuarios_influentes.append({
            'user': user,
            'followers_count': user.followers_count,
            'following_count': user.following_count,
            'posts_count': user.posts_count
        })
    
    # Dados para gráficos
    dias_labels = [str(item['dia']) for item in posts_por_dia] if posts_por_dia else []
    posts_por_dia_values = [item['total'] for item in posts_por_dia] if posts_por_dia else []
    
    reacoes_labels = [item['reaction_type'] for item in reacoes_por_tipo] if reacoes_por_tipo else []
    reacoes_values = [item['total'] for item in reacoes_por_tipo] if reacoes_por_tipo else []
    
    hashtags_labels = [item['hashtag__name'] for item in hashtags_populares[:5]] if hashtags_populares else []
    hashtags_values = [item['total_posts'] for item in hashtags_populares[:5]] if hashtags_populares else []
    
    contexto = {
        'total_posts': total_posts,
        'total_comments': total_comments,
        'total_likes': total_likes,
        'total_shares': total_shares,
        'total_users': total_users,
        'total_follows': total_follows,
        'total_hashtags': total_hashtags,
        'posts_30_dias': posts_30_dias,
        'posts_por_dia_labels': json.dumps(dias_labels),
        'posts_por_dia_values': json.dumps(posts_por_dia_values),
        'usuarios_mais_ativos': usuarios_mais_ativos,
        'posts_mais_populares': posts_mais_populares,
        'hashtags_populares': hashtags_populares,
        'posts_com_imagem': posts_com_imagem,
        'posts_com_video': posts_com_video,
        'posts_com_link': posts_com_link,
        'posts_fixados': posts_fixados,
        'reacoes_por_tipo': reacoes_por_tipo,
        'reacoes_labels': json.dumps(reacoes_labels),
        'reacoes_values': json.dumps(reacoes_values),
        'comentarios_populares': comentarios_populares,
        'usuarios_influentes': usuarios_influentes,
        'hashtags_labels': json.dumps(hashtags_labels),
        'hashtags_values': json.dumps(hashtags_values),
    }
    
    return render(request, 'reports/relatorio_rede_social.html', contexto)
