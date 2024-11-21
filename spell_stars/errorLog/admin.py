from django.contrib import admin
from django.utils.timezone import localtime
from .models import ErrorLog

@admin.register(ErrorLog)
class ErrorLogAdmin(admin.ModelAdmin):
    list_display = ('level', 'message_preview', 'formatted_created_at')
    list_filter = ('level', 'created_at')
    search_fields = ('message', 'traceback')
    readonly_fields = ('level', 'formatted_message', 'formatted_traceback', 'created_at')
    ordering = ('-created_at',)

    def message_preview(self, obj):
        return obj.message[:50]
    message_preview.short_description = 'Message Preview'

    def formatted_message(self, obj):
        return f"<pre>{obj.message}</pre>"
    formatted_message.short_description = 'Full Message'
    formatted_message.allow_tags = True

    def formatted_traceback(self, obj):
        return f"<pre>{obj.traceback}</pre>" if obj.traceback else "No traceback available"
    formatted_traceback.short_description = 'Traceback'
    formatted_traceback.allow_tags = True

    def formatted_created_at(self, obj):
        return localtime(obj.created_at).strftime('%Y-%m-%d %H:%M:%S')
    formatted_created_at.short_description = 'Created At (Local Time)'
