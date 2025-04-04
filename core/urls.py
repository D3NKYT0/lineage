"""core URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", include('home.urls')),
    
    path('app/auditor/', include('auditor.urls', namespace='auditor')),
    path("app/notifications/", include('notification.urls')),

    path("", include('serve_files.urls')),
    path("", include('admin_volt.urls')),

    path("admin/", admin.site.urls),
]

# Static/media routes
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Error handlers
handler400 = 'home.views.custom_400_view'
handler404 = 'home.views.custom_404_view'
handler500 = 'home.views.custom_500_view'
