from django import forms
from apps.lineage.server.models import ApiEndpointToggle


class ApiEndpointToggleForm(forms.ModelForm):
    """Formulário para configuração de endpoints da API"""
    
    class Meta:
        model = ApiEndpointToggle
        fields = [
            # Server endpoints
            'players_online', 'top_pvp', 'top_pk', 'top_clan', 'top_rich', 
            'top_online', 'top_level', 'olympiad_ranking', 'olympiad_all_heroes',
            'olympiad_current_heroes', 'grandboss_status', 'raidboss_status',
            'siege', 'siege_participants', 'boss_jewel_locations',
            
            # Authentication endpoints
            'auth_login', 'auth_refresh', 'auth_logout',
            
            # User endpoints
            'user_profile', 'user_change_password', 'user_dashboard', 'user_stats',
            
            # Search endpoints
            'search_character', 'search_item',
            
            # Game data endpoints
            'clan_detail', 'auction_items',
            
            # Server status endpoints
            'server_status',
            
            # API info endpoints
            'api_info',
            
            # Monitoring endpoints
            'health_check', 'hourly_metrics', 'daily_metrics', 
            'performance_metrics', 'slow_queries', 'cache_stats',
            
            # Administration endpoints
            'api_config', 'api_config_panel',
        ]
        widgets = {
            field: forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'data-endpoint': field,
            }) for field in fields
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Adiciona classes CSS e labels personalizados para cada campo
        for field_name in self.fields:
            field = self.fields[field_name]
            field.widget.attrs.update({
                'class': 'form-check-input',
                'id': f'id_{field_name}',
                'data-endpoint': field_name,
            })
            
            # Labels personalizados
            field_labels = {
                'players_online': 'Players Online',
                'top_pvp': 'Top PvP',
                'top_pk': 'Top PK',
                'top_clan': 'Top Clan',
                'top_rich': 'Top Rich',
                'top_online': 'Top Online',
                'top_level': 'Top Level',
                'olympiad_ranking': 'Olympiad Ranking',
                'olympiad_all_heroes': 'Olympiad All Heroes',
                'olympiad_current_heroes': 'Olympiad Current Heroes',
                'grandboss_status': 'Grand Boss Status',
                'raidboss_status': 'Raid Boss Status',
                'siege': 'Siege',
                'siege_participants': 'Siege Participants',
                'boss_jewel_locations': 'Boss Jewel Locations',
                'auth_login': 'Auth Login',
                'auth_refresh': 'Auth Refresh',
                'auth_logout': 'Auth Logout',
                'user_profile': 'User Profile',
                'user_change_password': 'User Change Password',
                'user_dashboard': 'User Dashboard',
                'user_stats': 'User Stats',
                'search_character': 'Search Character',
                'search_item': 'Search Item',
                'clan_detail': 'Clan Detail',
                'auction_items': 'Auction Items',
                'server_status': 'Server Status',
                'api_info': 'API Info',
                'health_check': 'Health Check',
                'hourly_metrics': 'Hourly Metrics',
                'daily_metrics': 'Daily Metrics',
                'performance_metrics': 'Performance Metrics',
                'slow_queries': 'Slow Queries',
                'cache_stats': 'Cache Stats',
                'api_config': 'API Config',
                'api_config_panel': 'API Config Panel',
            }
            
            field.label = field_labels.get(field_name, field_name.replace('_', ' ').title())
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
        return instance 