from django.db import models
from django.utils import timezone


class Team(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('competition', 'Competition'),
        ('inactive', 'Inactive'),
    )
    
    name = models.CharField(max_length=100)
    age_group = models.CharField(max_length=20)  # U8, U10, U12, U14, U16, Senior
    season = models.CharField(max_length=9, default='2025')
    
    # Staff
    head_coach = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, related_name='head_coached_teams')
    assistant_coaches = models.ManyToManyField('auth.User', related_name='assistant_coached_teams', blank=True)
    
    # Details
    disciplines = models.JSONField(default=list)  # ["sprints", "hurdles", "throws"]
    practice_schedule = models.JSONField(default=dict)  # {"monday": "4:00-6:00 PM", ...}
    team_color = models.CharField(max_length=7, default='#c8f135')  # hex color
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    max_athletes = models.IntegerField(default=30)
    current_athletes = models.IntegerField(default=0)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'teams'
        ordering = ['age_group', 'name']
        unique_together = [['name', 'season']]
    
    def __str__(self):
        return f"{self.name} ({self.season})"

class PracticeAttendance(models.Model):
    athlete = models.ForeignKey('athletes.Athlete', on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    practice_date = models.DateField()
    attended = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    marked_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)
    
    class Meta:
        db_table = 'practice_attendance'
        unique_together = [['athlete', 'team', 'practice_date']]


class TrainingSession(models.Model):
    SESSION_TYPE_CHOICES = (
        ('practice', 'Practice'),
        ('gym', 'Gym / Strength'),
        ('video', 'Video Review'),
        ('recovery', 'Recovery'),
        ('scrimmage', 'Scrimmage'),
        ('other', 'Other'),
    )
    RECURRENCE_CHOICES = (
        ('none', 'One-time'),
        ('weekly', 'Weekly'),
        ('biweekly', 'Bi-weekly'),
    )

    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='training_sessions')
    title = models.CharField(max_length=200)
    session_type = models.CharField(max_length=20, choices=SESSION_TYPE_CHOICES, default='practice')
    location = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)

    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()

    recurrence = models.CharField(max_length=20, choices=RECURRENCE_CHOICES, default='none')
    recurrence_days = models.JSONField(default=list, blank=True)  # [0,2,4] = Mon,Wed,Fri
    recurrence_end_date = models.DateField(null=True, blank=True)

    created_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, related_name='created_sessions')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'training_sessions'
        ordering = ['start_datetime']
        indexes = [
            models.Index(fields=['team', 'start_datetime']),
        ]

    def __str__(self):
        return f"{self.team} — {self.title} ({self.start_datetime.date()})"


class TransferRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    )

    athlete = models.ForeignKey('athletes.Athlete', on_delete=models.CASCADE, related_name='transfer_requests')
    from_team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name='outbound_transfers')
    to_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='inbound_transfers')
    requested_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, related_name='initiated_transfers')

    reason = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    reviewed_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_transfers')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    admin_notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'transfer_requests'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.athlete} → {self.to_team} ({self.status})"