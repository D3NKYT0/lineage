from django.contrib import admin
from core.admin import BaseModelAdmin
from .models import DownloadCategory, DownloadLink
from django.utils.translation import gettext_lazy as _

@admin.register(DownloadCategory)
class DownloadCategoryAdmin(BaseModelAdmin):
    list_display = ('name', 'description', 'order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    ordering = ('order', 'name')

@admin.register(DownloadLink)
class DownloadLinkAdmin(BaseModelAdmin):
    list_display = ('name', 'category', 'download_type', 'hosting_type', 'version', 'download_count', 'is_active')
    list_filter = ('category', 'download_type', 'hosting_type', 'is_active')
    search_fields = ('name', 'description', 'version')
    ordering = ('category', 'order', 'name')
    readonly_fields = ('download_count',) 