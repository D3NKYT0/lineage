from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from django.views.i18n import JavaScriptCatalog
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import redirect
from django.http import FileResponse, Http404
from django.views.decorators.cache import cache_control
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
import os

def admin_login_redirect(request):
    return redirect('login')

@cache_control(max_age=86400)  # Cache por 24 horas
def favicon_view(request):
    """Serve favicon.ico with proper caching"""
    try:
        favicon_path = os.path.join(settings.STATICFILES_DIRS[0], 'favicon.ico')
        if os.path.exists(favicon_path):
            return FileResponse(
                open(favicon_path, 'rb'), 
                content_type='image/x-icon'
            )
        else:
            raise Http404("Favicon not found")
    except Exception:
        raise Http404("Favicon not found")

urlpatterns = [
    # Favicon
    path('favicon.ico', favicon_view, name='favicon'),
    
    # main app start
    path('', include('apps.main.home.urls')),

    # api app
    path('api/', include('apps.api.urls')),

    # lience app
    path('licence/', include('apps.main.licence.urls')),
    path('social/', include('apps.main.social.urls')),
    path('resources/', include('apps.main.resources.urls')),
    
    # apps native
    path('app/message/', include('apps.main.message.urls')),
    path('app/', include('apps.main.administrator.urls')),
    path('app/news/', include('apps.main.news.urls')),
    path('app/faq/', include('apps.main.faq.urls')),
    path('app/auditor/', include('apps.main.auditor.urls')),
    path('app/notification/', include('apps.main.notification.urls')),
    path('app/solicitation/', include('apps.main.solicitation.urls')),
    path('app/calendary/', include('apps.main.calendary.urls')),
    path('', include('apps.main.downloads.urls')),

    # apps lineage
    path('app/wallet/', include('apps.lineage.wallet.urls')),
    path('app/payment/', include('apps.lineage.payment.urls')),
    path('app/server/', include('apps.lineage.server.urls')),
    path('app/accountancy/', include('apps.lineage.accountancy.urls')),
    path('app/inventory/', include('apps.lineage.inventory.urls')),
    path('app/shop/', include('apps.lineage.shop.urls')),
    path('app/auction/', include('apps.lineage.auction.urls')),
    path('app/game/', include('apps.lineage.games.urls')),
    path('app/report/', include('apps.lineage.reports.urls')),
    path('app/roadmap/', include('apps.lineage.roadmap.urls')),
    path('', include('apps.lineage.wiki.urls')),
    path('', include('apps.lineage.tops.urls')),

    # libs externals
    path('', include('serve_files.urls')),

    # libs core's
    path('admin/login/', admin_login_redirect, name='admin_login'),
    path('admin/', admin.site.urls),
    path('ckeditor5/', include('django_ckeditor_5.urls')),
    path('jsi18n/', JavaScriptCatalog.as_view(), name='jsi18n'),

    # API Documentation
    path('api/v1/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/v1/schema/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/v1/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    path('accounts/', include('allauth.urls')),
]

# Static/media routes
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static('/themes/', document_root=os.path.join(settings.BASE_DIR, 'themes'))

# Error handlers
handler400 = 'apps.main.home.views.commons.custom_400_view'
handler404 = 'apps.main.home.views.commons.custom_404_view'
handler500 = 'apps.main.home.views.commons.custom_500_view'
