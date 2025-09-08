from django.shortcuts import render, get_object_or_404
from .models import Roadmap
from apps.main.home.decorator import conditional_otp_required
from django.utils import translation


@conditional_otp_required
def index(request):
    # Exibe apenas itens publicados, não privados, e tradução em português
    language = translation.get_language()
    roadmaps = (
        Roadmap.objects.filter(is_published=True, is_private=False)
        .order_by('pub_date')
    )
    # Para cada roadmap, pega a tradução em português
    items = []
    for roadmap in roadmaps:
        translation_obj = roadmap.translations.filter(language=language).first() or roadmap.translations.filter(language='pt').first()
        if translation_obj:
            items.append({
                'roadmap': roadmap,
                'translation': translation_obj,
            })
    return render(request, 'pages/roadmap_index.html', {'items': items, 'segment': 'roadmap'})


@conditional_otp_required
def detail(request, slug):
    language = translation.get_language()
    roadmap = get_object_or_404(Roadmap, slug=slug, is_published=True, is_private=False)
    translation_obj = roadmap.translations.filter(language=language).first() or roadmap.translations.filter(language='pt').first()
    return render(request, 'pages/roadmap_detail.html', {
        'roadmap': roadmap,
        'translation': translation_obj,
    })
