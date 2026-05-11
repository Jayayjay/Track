from django.db import models

class Event(models.Model):
    EVENT_TYPES = (
        ('practice', 'Practice'),
        ('meet', 'Meet / Competition'),
        ('meeting', 'Meeting'),
        ('social', 'Social Event'),
        ('other', 'Other'),
    )
    
    name = models.CharField(max_length=200)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    description = models.TextField(blank=True)
    
    # Date & Time
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    registration_deadline = models.DateTimeField(null=True, blank=True)
    
    # Location
    venue_name = models.CharField(max_length=200)
    address = models.TextField()
    location_url = models.URLField(blank=True)
    
    # Participants
    teams = models.ManyToManyField('teams.Team', related_name='events', blank=True)
    all_teams = models.BooleanField(default=False)
    
    # Registration
    requires_registration = models.BooleanField(default=False)
    max_participants = models.IntegerField(null=True, blank=True)
    registration_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Status
    is_published = models.BooleanField(default=True)
    is_cancelled = models.BooleanField(default=False)
    cancellation_reason = models.TextField(blank=True)
    
    # Metadata
    created_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'events'
        ordering = ['start_datetime']
        indexes = [
            models.Index(fields=['start_datetime', 'end_datetime']),
            models.Index(fields=['event_type']),
        ]
    
    def __str__(self):
        return self.name

class EventRegistration(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('waitlisted', 'Waitlisted'),
        ('cancelled', 'Cancelled'),
        ('attended', 'Attended'),
    )
    
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    athlete = models.ForeignKey('athletes.Athlete', on_delete=models.CASCADE)
    registered_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_received = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'event_registrations'
        unique_together = [['event', 'athlete']]