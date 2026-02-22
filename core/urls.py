from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from django.views.i18n import JavaScriptCatalog
from django.shortcuts import redirect
from django.http import FileResponse, Http404, HttpResponse
from django.views.decorators.cache import cache_control
from django.views.decorators.http import require_GET
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
from drf_spectacular.utils import extend_schema

class CustomSchemaView(SpectacularAPIView):
    @extend_schema(
        summary="OpenAPI Schema",
        description="Retorna o schema oficial da API (OpenAPI 3.0) em formato YAML/JSON.",
        tags=["Schema"],
        auth=[],
        responses={200: dict}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
from apps.media_storage.views import serve_media
from core.telemetry_views import metrics_view
from django.utils.functional import cached_property
import os


# -------------------------------
# Utils / Helpers
# -------------------------------

class CachedFavicon:
    @cached_property
    def content(self):
        favicon_path = os.path.join(settings.STATICFILES_DIRS[0], "favicon.ico")
        with open(favicon_path, "rb") as f:
            return f.read()


favicon_cache = CachedFavicon()


@cache_control(max_age=86400)  # Cache por 24h
def favicon_view(request):
    return HttpResponse(favicon_cache.content, content_type="image/x-icon")


def admin_login_redirect(request):
    # Redirecionar admin login para o login do allauth
    return redirect("account_login")


@cache_control(max_age=604800)  # Cache por 7 dias
def serve_any_media(request, path):
    """Serve arquivos de mídia públicos (exceto media_storage)"""
    if path.startswith("media_storage/"):
        raise Http404("Arquivo não encontrado")

    file_path = os.path.join(settings.MEDIA_ROOT, path)
    try:
        return FileResponse(open(file_path, "rb"))
    except FileNotFoundError:
        raise Http404("Arquivo não encontrado")


# -------------------------------
# Patterns organizados
# -------------------------------

main_patterns = [
    path("", include("apps.main.home.urls")),
    path("downloads/", include("apps.main.downloads.urls")),
    path("licence/", include("apps.main.licence.urls")),
    path("social/", include("apps.main.social.urls")),
    path("resources/", include("apps.main.resources.urls")),
]

native_patterns = [
    path("message/", include("apps.main.message.urls")),
    path("", include("apps.main.administrator.urls")),
    path("news/", include("apps.main.news.urls")),
    path("faq/", include("apps.main.faq.urls")),
    path("auditor/", include("apps.main.auditor.urls")),
    path("notification/", include("apps.main.notification.urls")),
    path("solicitation/", include("apps.main.solicitation.urls")),
    path("calendary/", include("apps.main.calendary.urls")),
    path("ai-assistant/", include("apps.main.ai_assistant.urls")),
]

lineage_patterns = [
    path("wallet/", include("apps.lineage.wallet.urls")),
    path("payment/", include("apps.lineage.payment.urls")),
    path("server/", include("apps.lineage.server.urls")),
    path("accountancy/", include("apps.lineage.accountancy.urls")),
    path("inventory/", include("apps.lineage.inventory.urls")),
    path("shop/", include("apps.lineage.shop.urls")),
    path("marketplace/", include("apps.lineage.marketplace.urls")),
    path("auction/", include("apps.lineage.auction.urls")),
    path("game/", include("apps.lineage.games.urls")),
    path("report/", include("apps.lineage.reports.urls")),
    path("roadmap/", include("apps.lineage.roadmap.urls")),
    path("wiki/", include("apps.lineage.wiki.urls")),
    path("tops/", include("apps.lineage.tops.urls")),
    path("clans/", include("apps.lineage.clans.urls", namespace='clans')),
]


# -------------------------------
# URLS principais
# -------------------------------

urlpatterns = [
    # Favicon
    path("favicon.ico", favicon_view, name="favicon"),

    # Main
    path("", include(main_patterns)),

    # Native apps
    path("app/", include(native_patterns)),

    # Media storage
    path("app/media/", include("apps.media_storage.urls")),
    path("media/media_storage/<path:path>/", serve_media, name="media_file"),
    path("media/<path:path>/", serve_any_media, name="media_any"),

    # Lineage apps
    path("app/", include(lineage_patterns)),

    # API
    path("api/", include("apps.api.urls")),
    path("api/v1/schema/", CustomSchemaView.as_view(), name="schema"),
    path(
        "api/v1/schema/swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/v1/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),

    # Externals
    path("", include("serve_files.urls")),

    # Core
    path("admin/login/", admin_login_redirect, name="admin_login"),
    path("admin/", admin.site.urls),
    # Telemetria (métricas Prometheus) - path configurável em TELEMETRY_METRICS_PATH
    path("internal/metrics/", require_GET(metrics_view), name="telemetry_metrics"),
    path("ckeditor5/", include("django_ckeditor_5.urls")),
    path("jsi18n/", JavaScriptCatalog.as_view(), name="jsi18n"),
    path("accounts/", include("allauth.urls")),
]

# Static/themes
urlpatterns += static(
    "/themes/", document_root=os.path.join(settings.BASE_DIR, "themes")
)

# Error handlers
handler400 = "apps.main.home.views.commons.custom_400_view"
handler404 = "apps.main.home.views.commons.custom_404_view"
handler500 = "apps.main.home.views.commons.custom_500_view"
