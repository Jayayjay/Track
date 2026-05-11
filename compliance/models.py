from django.db import models
from django.utils import timezone


class ComplianceRecord(models.Model):
    """Tracks a compliance document or certification for a staff member or athlete."""

    RECORD_TYPE_CHOICES = (
        ('wwcc',             'Working With Children Check'),
        ('first_aid',        'First Aid Certificate'),
        ('coaching_license', 'Coaching License'),
        ('police_check',     'Police Background Check'),
        ('medical_clearance','Medical Clearance'),
        ('insurance',        'Insurance'),
        ('safeguarding',     'Safeguarding Training'),
        ('other',            'Other'),
    )
    STATUS_CHOICES = (
        ('valid',    'Valid'),
        ('expiring', 'Expiring Soon'),
        ('expired',  'Expired'),
        ('pending',  'Pending Review'),
        ('rejected', 'Rejected'),
    )

    user = models.ForeignKey(
        'auth.User', on_delete=models.CASCADE,
        related_name='compliance_records', null=True, blank=True,
    )
    athlete = models.ForeignKey(
        'athletes.Athlete', on_delete=models.CASCADE,
        related_name='compliance_records', null=True, blank=True,
    )
    record_type      = models.CharField(max_length=30, choices=RECORD_TYPE_CHOICES)
    document_number  = models.CharField(max_length=100, blank=True)
    issuing_body     = models.CharField(max_length=200, blank=True)
    issue_date       = models.DateField(null=True, blank=True)
    expiry_date      = models.DateField(null=True, blank=True)
    document_file    = models.FileField(upload_to='compliance/documents/', null=True, blank=True)
    status           = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes            = models.TextField(blank=True)

    verified_by = models.ForeignKey(
        'auth.User', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='verified_compliance_records',
    )
    verified_at      = models.DateTimeField(null=True, blank=True)
    reminder_sent_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'compliance_records'
        ordering = ['expiry_date']
        indexes = [
            models.Index(fields=['status', 'expiry_date']),
            models.Index(fields=['record_type']),
        ]

    def __str__(self):
        subject = self.user or self.athlete or 'Unknown'
        return f"{subject} — {self.get_record_type_display()} ({self.status})"

    @property
    def days_until_expiry(self):
        if not self.expiry_date:
            return None
        return (self.expiry_date - timezone.now().date()).days


class BackgroundCheck(models.Model):
    """Dedicated background check tracking with external provider reference."""

    STATUS_CHOICES = (
        ('pending',   'Pending'),
        ('submitted', 'Submitted to Provider'),
        ('clear',     'Clear'),
        ('flagged',   'Flagged'),
        ('expired',   'Expired'),
    )

    user             = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='background_checks')
    provider         = models.CharField(max_length=200, blank=True)
    reference_number = models.CharField(max_length=100, blank=True)
    submitted_date   = models.DateField(null=True, blank=True)
    cleared_date     = models.DateField(null=True, blank=True)
    expiry_date      = models.DateField(null=True, blank=True)
    status           = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes            = models.TextField(blank=True)
    document_file    = models.FileField(upload_to='compliance/background_checks/', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'background_checks'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} — Background Check ({self.status})"


class IncidentReport(models.Model):
    """Records a safety incident or injury that occurred at a club activity."""

    SEVERITY_CHOICES = (
        ('low',      'Low — Minor, no medical attention needed'),
        ('medium',   'Medium — First aid administered'),
        ('high',     'High — Medical / hospital required'),
        ('critical', 'Critical — Life threatening / emergency'),
    )
    STATUS_CHOICES = (
        ('open',        'Open'),
        ('under_review','Under Review'),
        ('resolved',    'Resolved'),
        ('escalated',   'Escalated'),
    )
    INCIDENT_TYPE_CHOICES = (
        ('injury',       'Injury'),
        ('near_miss',    'Near Miss'),
        ('safeguarding', 'Safeguarding Concern'),
        ('property',     'Property Damage'),
        ('behavioural',  'Behavioural'),
        ('other',        'Other'),
    )

    title         = models.CharField(max_length=200)
    incident_type = models.CharField(max_length=30, choices=INCIDENT_TYPE_CHOICES, default='injury')
    severity      = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='low')
    status        = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    incident_date = models.DateTimeField()
    location      = models.CharField(max_length=300, blank=True)

    involved_athlete = models.ForeignKey(
        'athletes.Athlete', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='incident_reports',
    )
    involved_user = models.ForeignKey(
        'auth.User', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='involved_incidents',
    )
    witnesses     = models.TextField(blank=True)
    description   = models.TextField()
    action_taken  = models.TextField(blank=True)

    follow_up_required = models.BooleanField(default=False)
    follow_up_notes    = models.TextField(blank=True)

    reported_by = models.ForeignKey(
        'auth.User', on_delete=models.SET_NULL, null=True,
        related_name='reported_incidents',
    )
    assigned_to = models.ForeignKey(
        'auth.User', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='assigned_incidents',
    )
    resolved_at      = models.DateTimeField(null=True, blank=True)
    escalated_at     = models.DateTimeField(null=True, blank=True)
    escalation_notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'incident_reports'
        ordering = ['-incident_date']
        indexes = [
            models.Index(fields=['status', 'severity']),
            models.Index(fields=['incident_date']),
        ]

    def __str__(self):
        return f"[{self.severity.upper()}] {self.title} — {self.incident_date.date()}"


class AuditLog(models.Model):
    """Immutable audit trail of admin and API actions."""

    ACTION_CHOICES = (
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('login',  'Login'),
        ('logout', 'Logout'),
        ('export', 'Data Export'),
        ('approve','Approve'),
        ('reject', 'Reject'),
        ('view',   'View'),
        ('other',  'Other'),
    )

    user        = models.ForeignKey(
        'auth.User', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='audit_logs',
    )
    action      = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model_name  = models.CharField(max_length=100)
    object_id   = models.CharField(max_length=50, blank=True)
    object_repr = models.CharField(max_length=300, blank=True)
    changes     = models.JSONField(default=dict, blank=True)
    ip_address  = models.GenericIPAddressField(null=True, blank=True)
    user_agent  = models.CharField(max_length=500, blank=True)
    timestamp   = models.DateTimeField(auto_now_add=True)
    notes       = models.TextField(blank=True)

    class Meta:
        db_table = 'audit_logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['model_name', 'object_id']),
            models.Index(fields=['user', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.user} {self.action} {self.model_name}:{self.object_id} @ {self.timestamp:%Y-%m-%d %H:%M}"
