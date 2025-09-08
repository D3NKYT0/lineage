from django.shortcuts import get_object_or_404
from django.http import Http404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from apps.main.faq.models import FAQ
from apps.main.news.models import News
from django.utils.translation import get_language, gettext as _
from utils.render_theme_page import render_theme_page
from django.shortcuts import redirect


def public_news_list(request):
    # Busca todas as notícias publicadas e públicas, ordenadas por data
    all_news = News.objects.filter(is_published=True, is_private=False).order_by('-pub_date')
    
    # Configuração da paginação
    paginator = Paginator(all_news, 12)  # 12 notícias por página
    page = request.GET.get('page')
    
    try:
        news_page = paginator.page(page)
    except PageNotAnInteger:
        # Se a página não for um número, mostra a primeira página
        news_page = paginator.page(1)
    except EmptyPage:
        # Se a página estiver fora do range, mostra a última página
        news_page = paginator.page(paginator.num_pages)

    language = get_language()
    news_with_translations = []

    for news in news_page:
        translation = news.translations.filter(language=language).first()
        if translation:
            news_with_translations.append({
                'news': news,
                'translation': translation
            })

    context = {
        'latest_news_list': news_with_translations,
        'news_page': news_page,
        'total_news': all_news.count(),
        'has_other_pages': news_page.has_other_pages(),
        'has_previous': news_page.has_previous(),
        'has_next': news_page.has_next(),
        'previous_page_number': news_page.previous_page_number() if news_page.has_previous() else None,
        'next_page_number': news_page.next_page_number() if news_page.has_next() else None,
        'current_page': news_page.number,
        'num_pages': paginator.num_pages,
    }

    return render_theme_page(request, 'public', 'news_index.html', context)


def public_news_detail(request, slug):
    news = get_object_or_404(News, slug=slug)
    if news.is_private and not request.user.is_authenticated:
        raise Http404(_("Notícia privada não está disponível."))

    language = get_language()
    translation = news.translations.filter(language=language).first()

    if not translation:
        raise Http404(_("Tradução não disponível para esta notícia."))

    context = {
        'news': news,
        'translation': translation
    }

    return render_theme_page(request, 'public', 'news_detail.html', context)


def public_faq_list(request):
    language = get_language()  # Obtém o idioma atual
    public_faqs = FAQ.objects.filter(is_public=True)

    # Obter traduções para o idioma atual
    translated_public_faqs = []
    for faq in public_faqs:
        translation = faq.translations.filter(language=language).first()
        if translation:
            translated_public_faqs.append(translation)

    context = {
        'public_faqs': translated_public_faqs,
    }

    return render_theme_page(request, 'public', 'faq.html', context)


def maintenance_view(request):
    """
    Página de manutenção para usuários comuns quando a licença está inválida
    """
    from django.shortcuts import render
    return render(request, 'public/maintenance_isolated.html', {})


def license_expired_view(request):
    """
    Página de licença expirada para superusuários
    """
    # Verifica se o usuário é superusuário
    if not request.user.is_authenticated or not request.user.is_superuser:
        # Se não for superusuário, redireciona para manutenção
        return redirect('maintenance')
    
    return render_theme_page(request, 'public', 'license_expired.html', {})
