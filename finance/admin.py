from django.contrib import admin
from .models import SeasonConfig, Payment, PaymentReminder, StripeTransaction

@admin.register(SeasonConfig)
class SeasonConfigAdmin(admin.ModelAdmin):
    list_display = ['season', 'standard_fee', 'early_bird_fee', 'registration_open_date', 'registration_close_date', 'is_active']
    list_editable = ['is_active']

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['athlete', 'season', 'amount', 'fee_tier', 'status', 'payment_method', 'due_date']
    list_filter = ['status', 'fee_tier', 'payment_method']
    search_fields = ['athlete__first_name', 'athlete__last_name', 'invoice_number']

@admin.register(PaymentReminder)
class PaymentReminderAdmin(admin.ModelAdmin):
    list_display = ['payment', 'reminder_type', 'sent_via', 'status', 'sent_at']

@admin.register(StripeTransaction)
class StripeTransactionAdmin(admin.ModelAdmin):
    list_display = ['stripe_payment_intent_id', 'amount', 'currency', 'status', 'created_at']
