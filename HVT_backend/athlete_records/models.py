from django.db import models

# Create your models here.
class AthleteRecords(models.Model):
    athlete_name = models.CharField(max_length=100)
    athlete_mark = models.DecimalField(max_digits=15, decimal_places=3)
    athlete_age = models.IntegerField()
    athlete_group = models.CharField(max_length=10)
    athlete_date = models.IntegerField()
    athlete_meet = models.CharField(max_length=100)
    
    class Meta:
        verbose_name = 'Athelete Records'
        
    def __str__(self):
        return f"ID:{self.id} - {self.athlete_meet}"
       