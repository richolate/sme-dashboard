from django.contrib import admin
from .models import UploadHistory


@admin.register(UploadHistory)
class UploadHistoryAdmin(admin.ModelAdmin):
    list_display = ('file_name', 'uploaded_by', 'status', 'total_rows', 
                    'successful_rows', 'failed_rows', 'created_at')
    list_filter = ('status', 'created_at', 'uploaded_by')
    search_fields = ('file_name', 'uploaded_by__username')
    readonly_fields = ('created_at', 'completed_at')
    date_hierarchy = 'created_at'
