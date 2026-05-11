from django.db import models
from django.contrib.auth.models import User
import datetime


class SeasonProgram(models.Model):
    name            = models.CharField(max_length=100, default='Summer Season')
    season          = models.CharField(max_length=20)               # e.g. "2025-26"
    fee             = models.DecimalField(max_digits=8, decimal_places=2, default=450.00)
    early_bird_fee  = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    early_bird_deadline = models.DateField(null=True, blank=True)
    registration_open   = models.DateField()
    registration_close  = models.DateField()
    is_active       = models.BooleanField(default=True)

    class Meta:
        ordering = ['-registration_open']

    def __str__(self):
        return f"Season {self.season} — {self.name}"

    def current_fee(self):
        today = datetime.date.today()
        if self.early_bird_fee and self.early_bird_deadline and today <= self.early_bird_deadline:
            return self.early_bird_fee
        return self.fee

    def current_fee_label(self):
        today = datetime.date.today()
        if self.early_bird_fee and self.early_bird_deadline and today <= self.early_bird_deadline:
            return 'Early Bird'
        return 'Standard'


class HQRegistration(models.Model):
    STATUS   = [('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')]
    GENDER   = [('M', 'Male'), ('F', 'Female'), ('NB', 'Non-binary'), ('P', 'Prefer not to say')]

    user     = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hq_registrations')
    program  = models.ForeignKey(SeasonProgram, on_delete=models.CASCADE)

    athlete_first_name   = models.CharField(max_length=100)
    athlete_last_name    = models.CharField(max_length=100)
    athlete_dob          = models.DateField()
    athlete_gender       = models.CharField(max_length=2, choices=GENDER)

    address              = models.CharField(max_length=200, blank=True)
    city                 = models.CharField(max_length=100, blank=True)
    state                = models.CharField(max_length=10,  blank=True)
    zip_code             = models.CharField(max_length=10,  blank=True)

    guardian_name         = models.CharField(max_length=200, blank=True)
    guardian_relationship = models.CharField(max_length=100, blank=True)
    guardian_phone        = models.CharField(max_length=20,  blank=True)
    guardian_email        = models.EmailField(blank=True)

    medical_notes  = models.TextField(blank=True)
    has_allergies  = models.BooleanField(default=False)
    allergies      = models.CharField(max_length=200, blank=True)

    waiver_accepted = models.BooleanField(default=False)
    photo_consent   = models.BooleanField(default=False)

    status     = models.CharField(max_length=20, choices=STATUS, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    PAYMENT_STATUS = [('unpaid','Unpaid'),('pending','Payment Pending'),('paid','Paid')]
    payment_status           = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='unpaid')
    stripe_payment_intent_id = models.CharField(max_length=200, blank=True)
    paid_at                  = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.athlete_first_name} {self.athlete_last_name} — {self.program}"
