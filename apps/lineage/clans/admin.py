from django.contrib import admin
from .models import ClanProfile, RecruitmentApplication

@admin.register(ClanProfile)
class ClanProfileAdmin(admin.ModelAdmin):
    list_display = ('clan_id', 'recruiting', 'focus', 'min_level', 'language')
    list_filter = ('recruiting', 'focus', 'language')
    search_fields = ('clan_id', 'motd')

@admin.register(RecruitmentApplication)
class RecruitmentApplicationAdmin(admin.ModelAdmin):
    list_display = ('char_name', 'char_id', 'clan_profile', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('char_name', 'char_id')
    readonly_fields = ('created_at',)
