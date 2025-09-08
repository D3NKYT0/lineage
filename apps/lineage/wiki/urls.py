from django.urls import path
from . import views

app_name = 'wiki'

urlpatterns = [
    # Home
    path('public/wiki/', views.WikiHomeView.as_view(), name='home'),
    
    # Updates (deve vir antes da URL genérica de páginas)
    path('public/wiki/updates/', views.WikiUpdateListView.as_view(), name='updates'),
    path('public/wiki/updates/<int:pk>/', views.WikiUpdateDetailView.as_view(), name='update_detail'),
    
    # Search (deve vir antes da URL genérica de páginas)
    path('public/wiki/search/', views.WikiSearchView.as_view(), name='search'),
    
    # Sitemap (deve vir antes da URL genérica de páginas)
    path('public/wiki/sitemap/', views.WikiSitemapView.as_view(), name='sitemap'),
    
    # Pages by content type
    path('public/wiki/type/<str:content_type>/', views.WikiPageListView.as_view(), name='pages_by_type'),
    
    # Individual pages (deve vir por último para não capturar URLs específicas)
    path('public/wiki/<slug:slug>/', views.WikiPageDetailView.as_view(), name='page'),
]
