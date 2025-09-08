from django.shortcuts import render, get_object_or_404, redirect
from .models import News
from django.utils import translation
from apps.main.home.decorator import conditional_otp_required
from .forms import NewsForm


@conditional_otp_required
def index(request):
    language = translation.get_language()
    private_news_list = News.objects.filter(is_published=True, is_private=True).order_by('-pub_date')[:5]

    # adiciona a tradução correta ou fallback em português
    translated_news = []
    for news in private_news_list:
        translation_obj = news.translations.filter(language=language).first() or news.translations.filter(language='pt').first()
        if translation_obj:
            translated_news.append({
                'news': news,
                'translation': translation_obj
            })

    context = {
        'private_news_list': translated_news,
        'segment': 'index',
        'parent': 'news',
    }
    return render(request, 'pages/news_index.html', context)


@conditional_otp_required
def detail(request, slug):
    language = translation.get_language()
    news = get_object_or_404(News, slug=slug)

    translation_obj = news.translations.filter(language=language).first() or news.translations.filter(language='pt').first()

    context = {
        'news': news,
        'translation': translation_obj,
        'segment': 'detail',
        'parent': 'news',
    }
    return render(request, 'pages/news_detail.html', context)


@conditional_otp_required
def create_news(request):
    if request.method == 'POST':
        form = NewsForm(request.POST, request.FILES)
        if form.is_valid():
            news = form.save(commit=False)
            news.author = request.user
            news.save()
            return redirect('news:detail', slug=news.slug)
    else:
        form = NewsForm()

    context = {
        'form': form,
        'segment': 'create',
        'parent': 'news',
    }
    return render(request, 'pages/news_create.html', context)
