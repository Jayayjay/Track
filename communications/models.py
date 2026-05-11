from django.db import models

class Announcement(models.Model):
    AUDIENCE_CHOICES = (
        ('all', 'All Members'),
        ('athletes', 'All Athletes'),
        ('parents', 'All Parents'),
        ('coaches', 'All Coaches'),
        ('team', 'Specific Team'),
    )
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    audience = models.CharField(max_length=20, choices=AUDIENCE_CHOICES)
    target_team = models.ForeignKey('teams.Team', on_delete=models.SET_NULL, null=True, blank=True)
    send_email = models.BooleanField(default=False)
    send_sms = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)
    published_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)
    published_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'announcements'
        ordering = ['-published_at']

class EmailAutomation(models.Model):
    name = models.CharField(max_length=100)
    trigger_type = models.CharField(max_length=50)  # registration, payment, event_reminder, waiver, overdue
    subject_template = models.CharField(max_length=200)
    body_template = models.TextField()
    is_active = models.BooleanField(default=True)
    delay_hours = models.IntegerField(default=0)  # delay before sending
    last_modified = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'email_automations'

class EmailLog(models.Model):
    recipient = models.EmailField()
    subject = models.CharField(max_length=200)
    template_used = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20)  # sent, failed, opened, bounced
    error_message = models.TextField(blank=True)
    sent_at = models.DateTimeField(auto_now_add=True)
    opened_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'email_logs'
        indexes = [
            models.Index(fields=['recipient', 'sent_at']),
        ]

class Notification(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=50)  # info, warning, success, error
    is_read = models.BooleanField(default=False)
    link = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']


class Conversation(models.Model):
    """A chat channel — one per team, or a direct message thread."""
    CONV_TYPE_CHOICES = (
        ('team',   'Team Channel'),
        ('direct', 'Direct Message'),
        ('group',  'Group Chat'),
    )

    name         = models.CharField(max_length=200, blank=True)
    conv_type    = models.CharField(max_length=20, choices=CONV_TYPE_CHOICES, default='team')
    team         = models.ForeignKey('teams.Team', on_delete=models.CASCADE, null=True, blank=True, related_name='conversations')
    participants = models.ManyToManyField('auth.User', related_name='conversations', blank=True)
    created_by   = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, related_name='created_conversations')
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'conversations'
        ordering = ['-created_at']

    def __str__(self):
        return self.name or f"{self.conv_type}:{self.id}"


class Message(models.Model):
    """A single chat message within a Conversation."""
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender       = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, related_name='sent_messages')
    content      = models.TextField()
    created_at   = models.DateTimeField(auto_now_add=True)
    is_deleted   = models.BooleanField(default=False)

    class Meta:
        db_table = 'messages'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['conversation', 'created_at']),
        ]

    def __str__(self):
        return f"{self.sender} @ {self.created_at:%H:%M}: {self.content[:60]}"