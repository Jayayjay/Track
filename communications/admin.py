from django.contrib import admin
from .models import Announcement, EmailAutomation, EmailLog, Notification, Conversation, Message

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', 'audience', 'target_team', 'is_published', 'published_by', 'published_at']
    list_filter = ['audience', 'is_published', 'send_email', 'send_sms']

@admin.register(EmailAutomation)
class EmailAutomationAdmin(admin.ModelAdmin):
    list_display = ['name', 'trigger_type', 'is_active', 'delay_hours']
    list_filter = ['is_active', 'trigger_type']

@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ['recipient', 'subject', 'status', 'sent_at']
    list_filter = ['status']
    search_fields = ['recipient', 'subject']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read']

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['name', 'conv_type', 'team', 'created_by', 'created_at']

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'conversation', 'created_at', 'is_deleted']
    list_filter = ['is_deleted']
