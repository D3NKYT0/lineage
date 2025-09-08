from .models import SiteLogo
import time

def site_logo(request):
    logo = SiteLogo.objects.filter(is_active=True).first()
    return {'site_logo': logo}

def timestamp_processor(request):
    """
    Context processor para adicionar timestamp em todos os templates
    para evitar cache de imagens criptografadas
    """
    return {
        'timestamp': int(time.time())
    }
