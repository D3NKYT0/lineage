"""
Configurações do Jazzmin - Admin Theme
Este arquivo contém todas as configurações relacionadas ao tema Jazzmin do Django Admin.
"""

from django.utils.translation import gettext_lazy as _

# =========================== JAZZMIN CONFIGURATION ===========================

def get_jazzmin_settings(project_title, project_logo):
    """
    Retorna as configurações do Jazzmin baseadas no título do projeto.
    
    Args:
        project_title (str): Título do projeto
        
    Returns:
        dict: Configurações do Jazzmin
    """
    return {
        # title of the window (Will default to current_admin_site.site_title if absent or None)
        "site_title": project_title,
        # Title on the login screen (19 chars max) (Will default to current_admin_site.site_header if absent or None)
        "site_header": project_title,
        # Title on the brand (19 chars max) (Will default to current_admin_site.site_header if absent or None)
        "site_brand": project_title,
        # Logo to use for your site, must be present in static files, used for brand on top left
        "site_logo": project_logo,
        # Logo to use for your site, must be present in static files, used for login form logo (defaults to site_logo)
        "login_logo": project_logo,
        # CSS classes that are applied to the logo above
        "site_logo_classes": "img-circle",
        # Relative path to a favicon for your site, will default to site_logo if absent (ideally 32x32 px)
        "site_icon": "assets/img/ico.jpg",
        # Welcome text on the login screen
        "welcome_sign": "Welcome to Panel Admin",
        # Copyright on the footer
        "copyright": "all rights reserved to " + project_title,
        # The model admin to search from the search bar, search bar omitted if excluded
        # "search_model": "auth.User",
        # Field name on user model that contains avatar ImageField/URLField/Charfield or a callable that receives the user
        "user_avatar": True,
        # URL for the login page
        "login_url": "login",
        # URL for the logout page
        "logout_url": "logout",
        # URL for the password change page
        "password_change_url": "password_change",
        # URL for the password reset page
        "password_reset_url": "password_reset",
        # Whether to show the UI customizer on the sidebar
        "show_ui_builder": False,
        ############
        # Top Menu #
        ############
        # Links to put along the top menu
        "topmenu_links": [
            {"name": "Home", "url": "admin:index", "permissions": ["auth.view_user"]},
            {"name": "Site Public", "url": "index"},
            {"name": "Site Private", "url": "dashboard"},
        ],
        #############
        # User Menu #
        #############
        # Links to put in the user menu
        "usermenu_links": [
            {"name": _("Meu Perfil"), "url": "profile", "icon": "fas fa-user"},
            {"name": _("Mudar Senha"), "url": "password_change", "icon": "fas fa-key"},
            {"name": _("Segurança"), "url": "administrator:security_settings", "icon": "fas fa-shield-alt"},
            {"name": _("Sair"), "url": "logout", "icon": "fas fa-sign-out-alt"},
        ],
        #############
        # Side Menu #
        #############
        # Whether to display the side menu
        "show_sidebar": True,
        # Whether to aut expand the menu
        "navigation_expanded": True,
        # Custom icons for side menu apps/models
        "icons": {
            # Auth
            "auth": "fas fa-users-cog",
            "auth.user": "fas fa-user",
            "auth.Group": "fas fa-users",
            
            # Administrator
            "administrator.ChatGroup": "fas fa-comments",
            "administrator.Theme": "fas fa-paint-brush",
            "administrator.BackgroundSetting": "fas fa-image",
            "administrator.ThemeVariable": "fas fa-palette",
            
            # Auditor
            "auditor.Auditor": "fas fa-history",
            
            # Calendary
            "calendary": "fas fa-calendar-alt",
            "calendary.Event": "fas fa-calendar-day",
            
            # FAQ
            "faq.FAQ": "fas fa-question-circle",
            "faq.FAQCategory": "fas fa-folder",
            "faq.FAQTranslation": "fas fa-language",
            
            # Home
            "home.User": "fas fa-user",
            "home.Profile": "fas fa-id-card",
            "home.State": "fas fa-map-marker-alt",
            "home.City": "fas fa-city",
            "home.DashboardContent": "fas fa-tachometer-alt",
            "home.user": "fas fa-user",
            "home.state": "fas fa-map-marker-alt",
            "home.city": "fas fa-city",
            "home.dashboardcontent": "fas fa-tachometer-alt",
            "home.dashboardcontenttranslation": "fas fa-language",
            "home.sitelogo": "fas fa-image",
            "home.conquista": "fas fa-trophy",
            "home.conquistausuario": "fas fa-medal",
            "home.perfilgamer": "fas fa-gamepad",
            "home.addressuser": "fas fa-map-marker-alt",
            "home.dashboardcontenttranslation": "fas fa-language",
            "home.siteLogo": "fas fa-image",
            "home.perfilgamer": "fas fa-gamepad",
            "home.conquista": "fas fa-trophy",
            "home.conquistausuario": "fas fa-medal",
            
            # Message
            "message.Friendship": "fas fa-user-friends",
            "message.Chat": "fas fa-comments",
            "message.Message": "fas fa-envelope",
            "message.MessageGroup": "fas fa-envelope-open",
            
            # News
            "news.News": "fas fa-newspaper",
            "news.NewsCategory": "fas fa-folder",
            "news.NewsTranslation": "fas fa-language",
            
            # Notification
            "notification.Notification": "fas fa-bell",
            "notification.PublicNotificationView": "fas fa-eye",
            "notification.PushSubscription": "fas fa-mobile-alt",
            "notification.PushNotificationLog": "fas fa-history",
            
            # Solicitation
            "solicitation.Solicitation": "fas fa-clipboard-list",
            "solicitation.SolicitationParticipant": "fas fa-users",
            "solicitation.SolicitationHistory": "fas fa-history",
            
            # Downloads
            "downloads.Download": "fas fa-download",
            "downloads.DownloadCategory": "fas fa-folder",
            "downloads.DownloadLink": "fas fa-download",
            
            # Wallet
            "wallet.Wallet": "fas fa-wallet",
            "wallet.TransacaoWallet": "fas fa-exchange-alt",
            "wallet.TransacaoBonus": "fas fa-gift",
            "wallet.CoinConfig": "fas fa-coins",
            "wallet.CoinPurchaseBonus": "fas fa-percentage",
            
            # Payment
            "payment.PedidoPagamento": "fas fa-money-bill-wave",
            "payment.Pagamento": "fas fa-credit-card",
            "payment.WebhookLog": "fas fa-history",
            
            # Accountancy
            "accountancy.Account": "fas fa-calculator",
            "accountancy.Transaction": "fas fa-file-invoice-dollar",
            
            # Inventory
            "inventory.Inventory": "fas fa-box",
            "inventory.InventoryItem": "fas fa-boxes",
            "inventory.BlockedServerItem": "fas fa-ban",
            "inventory.CustomItem": "fas fa-box-open",
            "inventory.InventoryLog": "fas fa-history",
            
            # Shop
            "shop.ShopItem": "fas fa-box-open",
            "shop.ShopPackage": "fas fa-box",
            "shop.ShopPackageItem": "fas fa-boxes",
            "shop.PromotionCode": "fas fa-tag",
            "shop.Cart": "fas fa-shopping-cart",
            "shop.CartItem": "fas fa-shopping-basket",
            "shop.CartPackage": "fas fa-boxes-stacked",
            "shop.ShopPurchase": "fas fa-receipt",
            "shop.PurchaseItem": "fas fa-shopping-bag",
            
            # Auction
            "auction.Auction": "fas fa-gavel",
            "auction.Bid": "fas fa-hand-holding-usd",
            
            # Games
            "games.Prize": "fas fa-trophy",
            "games.SpinHistory": "fas fa-history",
            "games.Bag": "fas fa-briefcase",
            "games.BagItem": "fas fa-box",
            "games.Item": "fas fa-box-open",
            "games.BoxType": "fas fa-boxes",
            "games.Box": "fas fa-gift",
            "games.BoxItem": "fas fa-boxes-stacked",
            "games.BoxItemHistory": "fas fa-history",
            "games.Recompensa": "fas fa-gift",
            "games.RecompensaRecebida": "fas fa-gift",
            "games.EconomyWeapon": "fas fa-khanda",
            "games.Monster": "fas fa-dragon",
            "games.RewardItem": "fas fa-gift",
            "games.BattlePassSeason": "fas fa-calendar-alt",
            "games.BattlePassLevel": "fas fa-level-up-alt",
            "games.BattlePassReward": "fas fa-medal",
            "games.UserBattlePassProgress": "fas fa-tasks",
            "games.BattlePassItemExchange": "fas fa-exchange-alt",

            # Roadmap
            "roadmap": "fas fa-route",
            "roadmap.Roadmap": "fas fa-map",
            "roadmap.RoadmapTranslation": "fas fa-map-marker-alt",

            # Externos / Libs
            "django_celery_results": "fas fa-tasks",
            "django_celery_results.TaskResult": "fas fa-tasks",
            "django_celery_results.GroupResult": "fas fa-layer-group",
            "account": "fas fa-user-circle",
            "account.EmailAddress": "fas fa-envelope",
            "account.EmailConfirmation": "fas fa-check-circle",
            "socialaccount": "fas fa-users",
            "socialaccount.SocialAccount": "fas fa-user-friends",
            "socialaccount.SocialApp": "fas fa-cogs",
            "socialaccount.SocialToken": "fas fa-key",
            "otp_totp": "fas fa-mobile-alt",
            "otp_totp.TOTPDevice": "fas fa-shield-alt",
            
            # Reports
            "reports.Report": "fas fa-chart-bar",
            "reports.ReportType": "fas fa-chart-line",
            
            # Wiki
            "wiki.WikiPage": "fas fa-book",
            "wiki.WikiSection": "fas fa-bookmark",
            "wiki.WikiUpdate": "fas fa-code-branch",
            "wiki.WikiEvent": "fas fa-calendar-alt",
            "wiki.WikiRate": "fas fa-percentage",
            "wiki.WikiFeature": "fas fa-star",
            "wiki.WikiGeneral": "fas fa-info-circle",
            "wiki.WikiRaid": "fas fa-dragon",
            "wiki.WikiAssistance": "fas fa-hands-helping",
            "wiki.WikiPageTranslation": "fas fa-language",
            "wiki.WikiSectionTranslation": "fas fa-language",
            "wiki.WikiUpdateTranslation": "fas fa-language",
            "wiki.WikiEventTranslation": "fas fa-language",
            "wiki.WikiRateTranslation": "fas fa-language",
            "wiki.WikiFeatureTranslation": "fas fa-language",
            "wiki.WikiGeneralTranslation": "fas fa-language",
            "wiki.WikiRaidTranslation": "fas fa-language",
            "wiki.WikiAssistanceTranslation": "fas fa-language",
            
            # Server
            "server.Server": "fas fa-server",
            "server.ServerStatus": "fas fa-signal",
            "server.ServerConfig": "fas fa-cogs",
            "server.ApiEndpointToggle": "fas fa-toggle-on",
            "server.ActiveAdenaExchangeItem": "fas fa-coins",
            "server.IndexConfig": "fas fa-cogs",
            "server.IndexConfigTranslation": "fas fa-language",
            "server.ServicePrice": "fas fa-tags",
            "server.Apoiador": "fas fa-star",
            "server.Comissao": "fas fa-percentage",
            "server.ApoiadorDefault": "fas fa-image",
            
            # Licence
            "licence": "fas fa-key",
            "licence.License": "fas fa-key",
            "licence.LicenseVerification": "fas fa-shield-alt",
            
            # Social
            "social.Post": "fas fa-share-alt",
            "social.Comment": "fas fa-comment",
            "social.CommentLike": "fas fa-heart",
            "social.Like": "fas fa-thumbs-up",
            "social.Share": "fas fa-share",
            "social.Follow": "fas fa-user-plus",
            "social.UserProfile": "fas fa-user-circle",
            "social.Hashtag": "fas fa-hashtag",
            "social.PostHashtag": "fas fa-tag",
            "social.Report": "fas fa-flag",
            "social.ReportFilterFlag": "fas fa-filter",
            "social.ModerationAction": "fas fa-gavel",
            "social.ContentFilter": "fas fa-shield-alt",
            "social.ModerationLog": "fas fa-clipboard-list",
        },
        # Icons that are used when one is not manually specified
        "default_icon_parents": "fas fa-chevron-circle-right",
        "default_icon_children": "fas fa-circle",
        #############
        # UI Tweaks #
        #############
        # Relative paths to custom CSS/JS files (must be present in static files)
        "custom_css": "custom/admin-custom.css",
        # "custom_js": "custom/admin-custom.js",
        ###############
        # Change view #
        ###############
        # Render out the change view as a single form, or in tabs, current options are
        # - single
        # - horizontal_tabs (default)
        # - vertical_tabs
        # - collapsible
        # - carousel
        "changeform_format": "horizontal_tabs",
        # override change forms on a per modeladmin basis
        "changeform_format_overrides": {
            "auth.user": "collapsible",
            "auth.group": "vertical_tabs",
        },
        # Add a language dropdown into the admin
        "language_chooser": False,
    }


def get_jazzmin_ui_tweaks():
    """
    Retorna as configurações de UI do Jazzmin.
    
    Returns:
        dict: Configurações de UI do Jazzmin
    """
    return {
        "navbar_small_text": False,
        "footer_small_text": False,
        "body_small_text": False,
        "brand_small_text": False,
        "brand_colour": "navbar-primary",
        "accent": "accent-primary",
        "navbar": "navbar-dark",
        "no_navbar_border": False,
        "navbar_fixed": True,
        "layout_boxed": False,
        "footer_fixed": False,
        "sidebar_fixed": True,
        "sidebar": "sidebar-dark-primary",
        "sidebar_nav_small_text": False,
        "sidebar_disable_expand": False,
        "sidebar_nav_child_indent": True,
        "sidebar_nav_compact_style": False,
        "sidebar_nav_legacy_style": False,
        "sidebar_nav_flat_style": False,
        "theme": "default",
        "dark_mode_theme": None,
        "button_classes": {
            "primary": "btn-primary",
            "secondary": "btn-secondary",
            "info": "btn-info",
            "warning": "btn-warning",
            "danger": "btn-danger",
            "success": "btn-success"
        }
    } 
