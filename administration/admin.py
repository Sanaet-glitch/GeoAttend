from django.contrib import admin
from .models import SystemSettings, AdminLog, StudentImportLog

@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    list_display = ('setting_key', 'setting_value', 'is_active', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('setting_key', 'setting_value')

@admin.register(AdminLog)
class AdminLogAdmin(admin.ModelAdmin):
    list_display = ('admin', 'action', 'object_type', 'object_id', 'timestamp')
    list_filter = ('action', 'timestamp', 'admin')
    search_fields = ('admin__username', 'object_type', 'details')
    date_hierarchy = 'timestamp'

@admin.register(StudentImportLog)
class StudentImportLogAdmin(admin.ModelAdmin):
    list_display = ('filename', 'admin', 'import_date', 'status', 'records_total', 'records_imported', 'records_failed')
    list_filter = ('status', 'import_date')
    search_fields = ('filename', 'admin__username')
    date_hierarchy = 'import_date'
