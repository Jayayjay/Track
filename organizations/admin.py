from django.contrib import admin
from .models import Organization, OrganizationMember

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'email', 'phone', 'is_active', 'created_at']
    search_fields = ['name', 'slug', 'email']
    list_filter = ['is_active']

@admin.register(OrganizationMember)
class OrganizationMemberAdmin(admin.ModelAdmin):
    list_display = ['user', 'organization', 'role', 'is_active', 'joined_at']
    list_filter = ['role', 'is_active']
