from django.db import models

class SeasonConfig(models.Model):
    season = models.CharField(max_length=9, unique=True)  # 2025
    registration_open_date = models.DateField()
    registration_close_date = models.DateField()
    standard_fee = models.DecimalField(max_digits=10, decimal_places=2, default=185.00)
    sibling_discount_fee = models.DecimalField(max_digits=10, decimal_places=2, default=155.00)
    scholarship_slots = models.IntegerField(default=20)
    scholarship_slots_used = models.IntegerField(default=0)
    early_bird_deadline = models.DateField(null=True, blank=True)
    early_bird_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    late_fee = models.DecimalField(max_digits=10, decimal_places=2, default=25.00)
    require_waiver = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'season_configs'
    
    def __str__(self):
        return f"Season {self.season}"

class Payment(models.Model):
    PAYMENT_STATUS = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('refunded', 'Refunded'),
        ('failed', 'Failed'),
    )
    
    PAYMENT_METHODS = (
        ('stripe', 'Stripe'),
        ('cash', 'Cash'),
        ('check', 'Check'),
        ('bank_transfer', 'Bank Transfer'),
    )
    
    FEE_TIERS = (
        ('standard', 'Standard'),
        ('sibling', 'Sibling Discount'),
        ('scholarship', 'Scholarship'),
        ('early_bird', 'Early Bird'),
    )
    
    athlete = models.ForeignKey('athletes.Athlete', on_delete=models.CASCADE, related_name='payments')
    season = models.ForeignKey(SeasonConfig, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    fee_tier = models.CharField(max_length=20, choices=FEE_TIERS)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, null=True, blank=True)
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    due_date = models.DateField()
    invoice_number = models.CharField(max_length=50, unique=True)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'payments'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'due_date']),
            models.Index(fields=['athlete', 'season']),
        ]
    
    def __str__(self):
        return f"{self.athlete.full_name} - {self.season.season} - ${self.amount}"

class PaymentReminder(models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='reminders')
    reminder_type = models.CharField(max_length=20)  # first, second, final
    sent_at = models.DateTimeField(auto_now_add=True)
    sent_via = models.CharField(max_length=20)  # email, sms
    status = models.CharField(max_length=20, default='sent')
    
    class Meta:
        db_table = 'payment_reminders'

class StripeTransaction(models.Model):
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, null=True, blank=True)
    stripe_payment_intent_id = models.CharField(max_length=255, unique=True)
    stripe_customer_id = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='usd')
    status = models.CharField(max_length=50)
    receipt_url = models.URLField(blank=True)
    created_at = models.DateTimeField()
    metadata = models.JSONField(default=dict)
    
    class Meta:
        db_table = 'stripe_transactions'