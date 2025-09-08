from django.shortcuts import render
from .models import FAQ
from django.utils.translation import get_language
from apps.main.home.decorator import conditional_otp_required


@conditional_otp_required
def faq_list(request):
    language = get_language()  # Obtém o idioma atual
    public_faqs = FAQ.objects.filter(is_public=True)
    private_faqs = FAQ.objects.filter(is_public=False)

    # Obter traduções para o idioma atual
    translated_public_faqs = []
    for faq in public_faqs:
        translation = faq.translations.filter(language=language).first()
        if translation:
            translated_public_faqs.append(translation)

    translated_private_faqs = []
    for faq in private_faqs:
        translation = faq.translations.filter(language=language).first()
        if translation:
            translated_private_faqs.append(translation)

    context = {
        'segment': 'index',
        'parent': 'faq',
        'public_faqs': translated_public_faqs,
        'private_faqs': translated_private_faqs if request.user.is_authenticated else [],
    }
    
    return render(request, 'pages/faq.html', context)
