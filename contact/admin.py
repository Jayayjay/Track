from django.contrib import admin
from .models import ContactMessage
# Register your models here.

class ContactMessageAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'email',
        'subject',
        'message',
        'created_at',
    ]
    
admin.site.register(ContactMessage, ContactMessageAdmin)