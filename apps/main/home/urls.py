from django.urls import path
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect

from .views.views import *
from .views.public import *
from .views.accounts import *
from .views.commons import *
from .views.wiki import *


urlpatterns = [
    # main index
    path('', index, name='index'),
    path('pages/dashboard/', dashboard, name="dashboard"),

    # internals views users
    path('app/profile/edit/', edit_profile, name='edit_profile'),
    path('app/profile/add-or-edit-address/', add_or_edit_address, name='add_or_edit_address'),
    path('app/profile/edit-avatar/', edit_avatar, name='edit_avatar'),
    path('app/profile/', profile, name='profile'),
    path('app/logs/info/', log_info_dashboard, name='log_info_dashboard'),
    path('app/logs/error/', log_error_dashboard, name='log_error_dashboard'),

    # public views
    path('public/news/', public_news_list, name='public_news_list'),
    path('public/news/<slug:slug>/', public_news_detail, name='public_news_detail'),
    path('public/faq/', public_faq_list, name='public_faq_list'),
    path("public/terms/", terms_view, name="terms"),
    path("public/user-agreement/", user_agreement_view, name="user_agreement"),
    path("public/privacy-policy/", privacy_policy_view, name="privacy_policy"),
    path("public/maintenance/", maintenance_view, name="maintenance"),
    path("public/license-expired/", license_expired_view, name="license_expired"),

    # Wiki views - Redirecting to new lineage wiki
    path('wiki/', lambda request: redirect('wiki:home'), name='wiki'),
    path('wiki/general/', lambda request: redirect('wiki:general'), name='wiki_general'),
    path('wiki/rates/', lambda request: redirect('wiki:rates'), name='wiki_rates'),
    path('wiki/raids/', lambda request: redirect('wiki:raids'), name='wiki_raids'),
    path('wiki/assistance/', lambda request: redirect('wiki:assistance'), name='wiki_assistance'),
    path('wiki/events/', lambda request: redirect('wiki:events'), name='wiki_events'),
    path('wiki/updates/', lambda request: redirect('wiki:updates'), name='updates'),
    path('wiki/features/', lambda request: redirect('wiki:features'), name='features'),

    # Authentication
    path('accounts/register/', register_view, name="register"),
    path('accounts/login/', UserLoginView.as_view(), name="login"),
    path('accounts/logout/', logout_view, name="logout"),
    path('accounts/password-change/', UserPasswordChangeView.as_view(), name='password_change'),
    path('accounts/password-change-done/', auth_views.PasswordChangeDoneView.as_view(template_name='accounts_custom/password-change-done.html'), name="password_change_done"),
    path('accounts/password-reset/', UserPasswordResetView.as_view(), name="password_reset"),
    path('accounts/password-reset-confirm/<uidb64>/<token>/', UserPasswrodResetConfirmView.as_view(), name="password_reset_confirm"),
    path('accounts/password-reset-done/', auth_views.PasswordResetDoneView.as_view(template_name='accounts_custom/password-reset-done.html'), name='password_reset_done'),
    path('accounts/password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='accounts_custom/password-reset-complete.html'), name='password_reset_complete'),
    path('accounts/lock/', lock, name="lock"),
    path('accounts/activate-lock/', activate_lock, name="activate_lock"),
    path('accounts/registration/success/', registration_success_view, name='registration_success'),
    path('accounts/2fa/', verify_2fa_view, name='verify_2fa'),
    path('accounts/activate-2fa/', ativar_2fa, name='ativar_2fa'),
    path('accounts/deactivate-2fa/', desativar_2fa, name='desativar_2fa'),

    # validations
    path('verify/<uidb64>/<token>/', verificar_email, name='verificar_email'),
    path('resend-verify/', reenviar_verificacao_view, name='reenviar_verificacao'),

    # locale
    path('set-language/', custom_set_language, name='set_language'),

    # disable views
    path('components/buttons/', empty_view, name="buttons"),
    path('components/notifications/', empty_view, name="notifications"),
    path('components/forms/', empty_view, name="forms"),
    path('components/modals/', empty_view, name="modals"),
    path('components/typography/', empty_view, name="typography"),
    path('pages/transaction/', empty_view, name="transaction"),
    path('pages/settings/', empty_view, name="settings"),
    path('tables/bs-tables/', empty_view, name="bs_tables"),
    path('pages/upgrade-to-pro/', empty_view, name="upgrade_to_pro"),
]
