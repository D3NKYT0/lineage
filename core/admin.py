from django.contrib import admin
from import_export.admin import ImportExportModelAdmin


class BaseModelAdmin(ImportExportModelAdmin):
    list_display = ('uuid', 'created_at', 'created_by', 'updated_at', 'updated_by')  # Incluindo o campo uuid
    readonly_fields = ('uuid', 'created_at', 'created_by', 'updated_at', 'updated_by')  # Tornando o campo uuid somente leitura

    def get_readonly_fields(self, request, obj=None):
        # Make fields read-only, but not in forms
        if obj:
            return self.readonly_fields
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        if not change:  # Se for um novo objeto
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


class BaseInlineAdmin(admin.StackedInline):
    """Classe base para inlines com configurações padrão"""
    extra = 0  # Não adiciona linhas vazias automaticamente


class BaseTabularInlineAdmin(admin.TabularInline):
    """Classe base para inlines tabulares com configurações padrão"""
    extra = 0  # Não adiciona linhas vazias automaticamente


class BaseModelAdminAbstratic(ImportExportModelAdmin):
    list_display = ('created_at', 'created_by', 'updated_at', 'updated_by')
    readonly_fields = ('created_at', 'created_by', 'updated_at', 'updated_by')

    def get_readonly_fields(self, request, obj=None):
        # Make fields read-only, but not in forms
        if obj:
            return self.readonly_fields
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        if not change:  # Se for um novo objeto
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
