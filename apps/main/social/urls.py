from django.urls import path
from . import views

app_name = 'social'

urlpatterns = [
    # Feed e posts
    path('feed/', views.feed, name='feed'),
    path('my-posts/', views.my_posts, name='my_posts'),
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
    
    # CRUD de posts
    path('post/create/', views.PostCreateView.as_view(), name='post_create'),
    path('post/<int:pk>/edit/', views.PostUpdateView.as_view(), name='post_edit'),
    path('post/<int:pk>/delete/', views.PostDeleteView.as_view(), name='post_delete'),
    
    # Interações
    path('post/<int:post_id>/like/', views.like_post, name='like_post'),
    path('post/<int:post_id>/react/', views.react_to_post, name='react_to_post'),
    path('post/<int:post_id>/share/', views.share_post, name='share_post'),
    path('post/<int:post_id>/pin/', views.pin_post, name='pin_post'),
    path('user/<int:user_id>/follow/', views.follow_user, name='follow_user'),
    path('comment/<int:comment_id>/like/', views.like_comment, name='like_comment'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    
    # Perfis
    path('profile/<str:username>/', views.user_profile, name='user_profile'),
    path('profile/<str:username>/followers/', views.followers_list, name='followers_list'),
    path('profile/<str:username>/following/', views.following_list, name='following_list'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    
    # Busca e hashtags
    path('search/', views.search, name='search'),
    path('hashtag/<str:hashtag_name>/', views.hashtag_detail, name='hashtag_detail'),
    
    # ============================================================================
    # URLs DE MODERAÇÃO
    # ============================================================================
    
    # Denúncias
    path('report/<str:content_type>/<int:content_id>/', views.report_content, name='report_content'),
    
    # Painel de moderação
    path('moderation/', views.moderation_dashboard, name='moderation_dashboard'),
    path('moderation/reports/', views.reports_list, name='reports_list'),
    path('moderation/reports/<int:report_id>/', views.report_detail, name='report_detail'),
    path('moderation/reports/<int:report_id>/update-status/', views.update_report_status, name='update_report_status'),
    path('moderation/reports/<int:report_id>/assign/', views.assign_report, name='assign_report'),
    
    # Filtros de conteúdo
    path('moderation/filters/', views.content_filters, name='content_filters'),
    path('moderation/filters/<int:filter_id>/edit/', views.edit_filter, name='edit_filter'),
    path('moderation/filters/<int:filter_id>/toggle/', views.toggle_filter, name='toggle_filter'),
    path('moderation/filters/<int:filter_id>/delete/', views.delete_filter, name='delete_filter'),
    path('moderation/filters/test/', views.test_content_filter, name='test_content_filter'),
    
    # Logs e ações
    path('moderation/logs/', views.moderation_logs, name='moderation_logs'),
    path('moderation/logs/export/excel/', views.export_logs_excel, name='export_logs_excel'),
    path('moderation/logs/export/csv/', views.export_logs_csv, name='export_logs_csv'),
    path('moderation/apply-retroactive/', views.apply_retroactive_filters, name='apply_retroactive_filters'),
    path('moderation/bulk-action/', views.bulk_moderation_action, name='bulk_moderation_action'),
    
    # ============================================================================
    # URLs DE VERIFICAÇÃO DE CONTA
    # ============================================================================
    
    # Solicitação e status
    path('verification/request/', views.verification_request_view, name='verification_request'),
    path('verification/status/', views.verification_status_view, name='verification_status'),
    path('verification/cancel/<int:request_id>/', views.verification_cancel_view, name='verification_cancel'),
    
    # Painel administrativo
    path('verification/admin/', views.verification_admin_list_view, name='verification_admin_list'),
    path('verification/admin/<int:request_id>/', views.verification_admin_detail_view, name='verification_admin_detail'),
    path('verification/admin/bulk-action/', views.verification_admin_bulk_action_view, name='verification_admin_bulk_action'),
]
