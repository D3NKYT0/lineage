from django.conf import settings
import os
from django.utils.text import slugify
from django.templatetags.static import static
from django.utils.translation import get_language


def project_metadata(request):
    return {
        'PROJECT_TITLE': settings.PROJECT_TITLE,
        'PROJECT_AUTHOR': settings.PROJECT_AUTHOR,
        'PROJECT_DESCRIPTION': settings.PROJECT_DESCRIPTION,
        'PROJECT_KEYWORDS': settings.PROJECT_KEYWORDS,
        'PROJECT_URL': settings.PROJECT_URL,
        'PROJECT_LOGO_URL': settings.PROJECT_LOGO_URL,
        'PROJECT_FAVICON_ICO': settings.PROJECT_FAVICON_ICO,
        'PROJECT_FAVICON_MANIFEST': settings.PROJECT_FAVICON_MANIFEST,
        'PROJECT_THEME_COLOR': settings.PROJECT_THEME_COLOR,
        'PROJECT_DISCORD_URL': settings.PROJECT_DISCORD_URL,
        'PROJECT_YOUTUBE_URL': settings.PROJECT_YOUTUBE_URL,
        'PROJECT_FACEBOOK_URL': settings.PROJECT_FACEBOOK_URL,
        'PROJECT_INSTAGRAM_URL': settings.PROJECT_INSTAGRAM_URL,
        'project_name': settings.PROJECT_NAME if hasattr(settings, 'PROJECT_NAME') else 'Lineage2',
        'version': settings.VERSION if hasattr(settings, 'VERSION') else '1.0.0',
    }


def active_theme(request):
    from apps.main.administrator.models import Theme

    theme = Theme.objects.filter(ativo=True).first()
    base_template = "layouts/base-default.html"
    theme_files = {}

    if theme:
        safe_slug = slugify(theme.slug)
        theme_path = os.path.join(settings.BASE_DIR, 'themes', 'installed', safe_slug)

        if os.path.isdir(theme_path):
            theme_files = {
                f: os.path.join('installed', safe_slug, f)
                for f in os.listdir(theme_path)
                if os.path.isfile(os.path.join(theme_path, f))
            }

        base_template = f"installed/{safe_slug}/base.html"
    
    return {
        'active_theme': safe_slug if theme else None,
        'base_template': base_template,
        'theme_slug': safe_slug if theme else None,
        'path_theme': f'/themes/installed/{safe_slug}' if theme else None,
        'theme_files': theme_files,
    }


def background_setting(request):
    from apps.main.administrator.models import BackgroundSetting

    bg = BackgroundSetting.get_active()
    if bg and bg.image:
        bg_url = bg.image.url
    else:
        bg_url = static('assets/img/l2/bgs/bg.png')  # Caminho padrão

    return {
        'background_url': bg_url
    }


def theme_variables(request):
    from apps.main.administrator.models import ThemeVariable

    lang_code = get_language()[:2]  # exemplo: 'pt', 'en', 'es'

    variables = ThemeVariable.objects.all()
    context = {var.nome: var.get_valor_convertido(lang_code) for var in variables}
    return context


def slogan_flag(request):
    return {
        'SHOW_SLOGAN': settings.SLOGAN
    }


def social_login_config(request):
    """Context processor para configurações de login social"""
    return {
        'SOCIAL_LOGIN_ENABLED': getattr(settings, 'SOCIAL_LOGIN_ENABLED', True),
        'SOCIAL_LOGIN_GOOGLE_ENABLED': getattr(settings, 'SOCIAL_LOGIN_GOOGLE_ENABLED', True),
        'SOCIAL_LOGIN_GITHUB_ENABLED': getattr(settings, 'SOCIAL_LOGIN_GITHUB_ENABLED', True),
        'SOCIAL_LOGIN_DISCORD_ENABLED': getattr(settings, 'SOCIAL_LOGIN_DISCORD_ENABLED', True),
        'SOCIAL_LOGIN_SHOW_SECTION': getattr(settings, 'SOCIAL_LOGIN_SHOW_SECTION', True),
    }
