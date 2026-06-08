from django.contrib import admin
from userauth.models import Complaint

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('complaint_id', 'user', 'category', 'priority', 'status', 'created_at')
    list_filter = ('status', 'priority', 'category')
    search_fields = ('complaint_id', 'user__username', 'description')
    readonly_fields = ('complaint_id', 'created_at', 'updated_at')
    fieldsets = (
        ('Complaint Information', {
            'fields': ('complaint_id', 'user', 'category', 'priority', 'description')
        }),
        ('Status Information', {
            'fields': ('status', 'assigned_to', 'remarks')
        }),
        ('Evidence', {
            'fields': ('evidence', 'evidence_name'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )