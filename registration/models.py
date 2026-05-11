from django.db import models


class RegistrationFormConfig(models.Model):
    season = models.ForeignKey('finance.SeasonConfig', on_delete=models.CASCADE, related_name='form_configs')
    field_name = models.CharField(max_length=100)
    field_label = models.CharField(max_length=200)
    field_type = models.CharField(max_length=50)  # text, date, select, checkbox
    is_required = models.BooleanField(default=False)
    is_enabled = models.BooleanField(default=True)
    options = models.JSONField(default=list, blank=True)
    order = models.IntegerField(default=0)

    class Meta:
        db_table = 'registration_form_configs'
        ordering = ['order']
        unique_together = [['season', 'field_name']]


class RegistrationSubmission(models.Model):
    season = models.ForeignKey('finance.SeasonConfig', on_delete=models.CASCADE)
    athlete = models.ForeignKey('athletes.Athlete', on_delete=models.CASCADE, null=True, blank=True)
    submitted_by = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    form_data = models.JSONField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='pending')  # pending, approved, rejected
    reviewed_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, related_name='reviewed_submissions')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'registration_submissions'
        ordering = ['-submitted_at']


class RegistrationOrder(models.Model):
    """Stores all SportsEngine / external registration order data per athlete-season."""

    ORDER_STATUS_CHOICES = (
        ('active', 'Active'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
        ('pending', 'Pending'),
    )

    athlete = models.ForeignKey('athletes.Athlete', on_delete=models.CASCADE, related_name='registration_orders')
    season = models.ForeignKey('finance.SeasonConfig', on_delete=models.SET_NULL, null=True, blank=True)

    # Order identifiers
    order_number = models.CharField(max_length=100, blank=True)
    entry_number = models.CharField(max_length=100, blank=True)
    sportsengine_id = models.CharField(max_length=100, blank=True)

    # Account / status
    account_email = models.EmailField(blank=True)
    order_status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='active')
    entry_status = models.CharField(max_length=50, blank=True)
    unclaimed_profiles = models.CharField(max_length=100, blank=True)

    # Classification
    sport = models.CharField(max_length=100, blank=True)
    registration_type = models.CharField(max_length=100, blank=True)   # Season Play, Tournament, etc.
    registrant_type = models.CharField(max_length=100, blank=True)     # Dependent-Athlete, etc.

    # Volunteer
    volunteer_willing = models.BooleanField(null=True, blank=True)

    # Financial — all nullable since imports may omit them
    registration_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    gross = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    net = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    service_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    gross_outstanding = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    net_outstanding = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    service_fee_outstanding = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount_names = models.CharField(max_length=500, blank=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    refunds = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    credits = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    registration_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'registration_orders'
        ordering = ['-registration_date', '-created_at']

    def __str__(self):
        return f"Order {self.order_number or self.entry_number} — {self.athlete.full_name}"


class Waiver(models.Model):
    """Waiver record linked to an athlete registration."""

    athlete = models.ForeignKey('athletes.Athlete', on_delete=models.CASCADE, related_name='waivers')
    season = models.ForeignKey('finance.SeasonConfig', on_delete=models.SET_NULL, null=True, blank=True)
    pdf_file = models.FileField(upload_to='waivers/%Y/%m/', null=True, blank=True)
    signed_by_name = models.CharField(max_length=200, blank=True)
    signed_by_relationship = models.CharField(max_length=100, blank=True)
    signed_at = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'waivers'
        ordering = ['-signed_at']

    def __str__(self):
        return f"Waiver — {self.athlete.full_name} ({self.season})"


class BulkImportLog(models.Model):
    uploaded_by = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    filename = models.CharField(max_length=255)
    import_type = models.CharField(max_length=50, default='generic')  # generic, sportsengine
    total_records = models.IntegerField()
    successful_records = models.IntegerField()
    failed_records = models.IntegerField()
    errors = models.JSONField(default=list)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'bulk_import_logs'
