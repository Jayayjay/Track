from django.db import models


class AnalyticsSnapshot(models.Model):
    """
    Nightly aggregated metric value.
    One row per (date, metric_name, dimension_key) combination.
    breakdown stores sub-groupings as JSON (e.g. per-team, per-age-group).
    """
    METRIC_CHOICES = (
        ('registrations_total',    'Total Registrations'),
        ('registrations_by_team',  'Registrations by Team'),
        ('registrations_by_age',   'Registrations by Age Group'),
        ('revenue_collected',      'Revenue Collected'),
        ('revenue_pending',        'Revenue Pending'),
        ('revenue_overdue',        'Revenue Overdue'),
        ('collection_rate',        'Collection Rate %'),
        ('athletes_active',        'Active Athletes'),
        ('athletes_by_team',       'Athletes by Team'),
        ('attendance_rate',        'Training Attendance Rate %'),
        ('compliance_valid',       'Compliance Records Valid'),
        ('compliance_expiring',    'Compliance Records Expiring'),
        ('compliance_expired',     'Compliance Records Expired'),
        ('incidents_open',         'Open Incidents'),
        ('transfers_pending',      'Pending Transfers'),
    )

    date         = models.DateField()
    metric_name  = models.CharField(max_length=60, choices=METRIC_CHOICES)
    dimension    = models.CharField(max_length=100, blank=True, default='')  # e.g. team name, age group
    value        = models.DecimalField(max_digits=14, decimal_places=4, default=0)
    breakdown    = models.JSONField(default=dict, blank=True)

    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'analytics_snapshots'
        unique_together = [['date', 'metric_name', 'dimension']]
        ordering = ['-date', 'metric_name']
        indexes = [
            models.Index(fields=['metric_name', 'date']),
        ]

    def __str__(self):
        dim = f' [{self.dimension}]' if self.dimension else ''
        return f"{self.date} · {self.metric_name}{dim} = {self.value}"
