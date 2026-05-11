from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Athlete(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
    )

    JERSEY_SIZES = (
        ('YXS', 'Youth XS'), ('YS', 'Youth S'), ('YM', 'Youth M'),
        ('YL', 'Youth L'), ('YXL', 'Youth XL'), ('S', 'Adult S'),
        ('M', 'Adult M'), ('L', 'Adult L'), ('XL', 'Adult XL'),
        ('XXL', 'Adult XXL'),
    )

    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
        ('graduated', 'Graduated'),
    )

    # Personal Info
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=2, choices=GENDER_CHOICES)
    jersey_size = models.CharField(max_length=4, choices=JERSEY_SIZES, blank=True)
    jersey_number = models.IntegerField(null=True, blank=True)
    # Uniform sizes from SportsEngine
    tank_size = models.CharField(max_length=30, blank=True)
    shorts_size = models.CharField(max_length=30, blank=True)

    # Address
    street_address_1 = models.CharField(max_length=200, blank=True)
    street_address_2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state_province = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True, default='United States')

    # Relationships
    team = models.ForeignKey('teams.Team', on_delete=models.SET_NULL, null=True, blank=True, related_name='athletes')
    primary_contact = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='dependent_athletes')
    secondary_contacts = models.ManyToManyField('auth.User', related_name='secondary_athletes', blank=True)

    # Legacy embedded emergency contact (kept for backward compat; use EmergencyContact model for new records)
    emergency_contact_name = models.CharField(max_length=200, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    emergency_contact_relationship = models.CharField(max_length=50, blank=True)
    secondary_contact_phone = models.CharField(max_length=20, blank=True)

    # Medical Info
    medical_notes = models.TextField(blank=True)
    medications = models.TextField(blank=True)
    # Allergies
    has_allergies = models.BooleanField(null=True, blank=True)
    allergies = models.TextField(blank=True)
    allergy_1 = models.CharField(max_length=200, blank=True)
    allergy_2 = models.CharField(max_length=200, blank=True)
    allergy_3 = models.CharField(max_length=200, blank=True)
    allergy_4 = models.CharField(max_length=200, blank=True)
    # Medical conditions
    has_medical_conditions = models.BooleanField(null=True, blank=True)
    medical_condition_1 = models.CharField(max_length=200, blank=True)
    medical_condition_2 = models.CharField(max_length=200, blank=True)
    medical_condition_3 = models.CharField(max_length=200, blank=True)
    medical_condition_4 = models.CharField(max_length=200, blank=True)

    # Physician
    physician_name = models.CharField(max_length=200, blank=True)
    physician_first_name = models.CharField(max_length=100, blank=True)
    physician_last_name = models.CharField(max_length=100, blank=True)
    physician_phone = models.CharField(max_length=20, blank=True)
    physician_phone_2 = models.CharField(max_length=20, blank=True)
    hospital_of_choice = models.CharField(max_length=200, blank=True)

    # Insurance
    insurance_provider = models.CharField(max_length=100, blank=True)
    insurance_group_number = models.CharField(max_length=100, blank=True)
    insurance_policy_number = models.CharField(max_length=100, blank=True)
    insurance_policy_holder = models.CharField(max_length=200, blank=True)
    insurance_phone = models.CharField(max_length=20, blank=True)

    # Contact
    secondary_email = models.EmailField(blank=True)
    volunteer_willing = models.BooleanField(null=True, blank=True)

    # Platform IDs
    sportsengine_id = models.CharField(max_length=100, blank=True, db_index=True)
    player_profile_id = models.CharField(max_length=100, blank=True)

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    waiver_signed = models.BooleanField(default=False)
    waiver_signed_date = models.DateField(null=True, blank=True)

    # Metadata
    registration_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    profile_photo = models.ImageField(upload_to='athletes/', null=True, blank=True)

    class Meta:
        db_table = 'athletes'
        ordering = ['last_name', 'first_name']
        indexes = [
            models.Index(fields=['team', 'status']),
            models.Index(fields=['last_name', 'first_name']),
        ]

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def age(self):
        from datetime import date
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )

    def __str__(self):
        return self.full_name


class Guardian(models.Model):
    athlete = models.ForeignKey(Athlete, on_delete=models.CASCADE, related_name='guardians')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True)
    cell_phone = models.CharField(max_length=30, blank=True)
    home_phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    order = models.PositiveSmallIntegerField(default=1)  # 1 = primary, 2 = secondary

    class Meta:
        db_table = 'guardians'
        ordering = ['order']

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def __str__(self):
        return f"{self.full_name} (Guardian of {self.athlete.full_name})"


class EmergencyContact(models.Model):
    athlete = models.ForeignKey(Athlete, on_delete=models.CASCADE, related_name='emergency_contacts')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True)
    relationship = models.CharField(max_length=100, blank=True)
    home_phone = models.CharField(max_length=30, blank=True)
    work_phone = models.CharField(max_length=30, blank=True)
    order = models.PositiveSmallIntegerField(default=1)  # 1 = primary, 2 = secondary

    class Meta:
        db_table = 'emergency_contacts'
        ordering = ['order']

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def __str__(self):
        return f"{self.full_name} — {self.relationship} (EC for {self.athlete.full_name})"


class AthleteDocument(models.Model):
    DOCUMENT_TYPES = (
        ('birth_cert', 'Birth Certificate'),
        ('waiver', 'Waiver Form'),
        ('medical', 'Medical Clearance'),
        ('photo_release', 'Photo Release'),
        ('report_card', 'Report Card'),
    )

    athlete = models.ForeignKey(Athlete, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    file = models.FileField(upload_to='athlete_docs/%Y/%m/')
    uploaded_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    class Meta:
        db_table = 'athlete_documents'
