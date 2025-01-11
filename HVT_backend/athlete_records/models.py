from django.db import models

# Create your models here.
class AthleteRecords(models.Model):
    CLASS = {
        '40 Yard Dash' : '40 Yard Dash',
       '50 Meter Dash':'50 Meter Dash',
       '100 Meters':'100 Meters',
       '200 Meters':'200 Meters',
       '400 Meters': '400 Meters',
       '800 Meters' : '800 Meters',
       '1500 Meters' : '1500 Meters', 
       '3000 Meters' : '3000 Meters',
       '80m Hurdles -39 inches' : '80m Hurdles -39 inches',
       '80m Hurdles -30 inches' : '80m Hurdles -30 inches',
       '80m Hurdles -33 inches' : '80m Hurdles -33 inches',
       '100m Hurdles - 39 inches' : '100m Hurdles - 39 inches',
       '100m Hurdles - 33 inches' : '100m Hurdles - 33 inches',
       '100m Hurdles - 30 inches' : '100m Hurdles - 30 inches',
       '110m Hurdles - 39 inches' : '110m Hurdles - 39 inches',
       '110m Hurdles - 42 inches' : '110m Hurdles - 42 inches',
       '200m Hurdles - 36 inches' : '200m Hurdles - 36 inches',
       '200m Hurdles - 30 inches' : '200m Hurdles - 30 inches',
       '400m Hurdles - 36 inches' : '400m Hurdles - 36 inches',
       '2k Steeplechase - 838mm': '2k Steeplechase - 838mm',
       '4x100 Relay' : '4x100 Relay',
       '4x400 Relay' : '4x400 Relay',
       '4x800 Relay' : '4x800 Relay',
       'Shot Put - 12lb' : 'Shot Put - 12lb',
       'Shot Put - 2kg' : 'Shot Put - 2kg',
       'Shot Put - 6lb' : 'Shot Put - 6lb',
       'Shot Put - 8lb' : 'Shot Put - 8lb',
       'Shot Put - 4kg' : 'Shot Put - 4kg',
       'Shot Put - 16lb' : 'Shot Put - 16lb',
       'Discuss - 1.6kg' : 'Discuss - 1.6kg',
       'Discuss - 1kg' : 'Discuss - 1kg',
       'Javelin - 800g' : 'Javelin - 800g',
       'Javelin - 300g TJ' : 'Javelin - 300g TJ',
       'Javelin - 300g' : 'Javelin - 300g',
       'Javelin - 450g AeroJav' : 'Javelin - 450g AeroJav',
       'Javelin - 600g' : 'Javelin - 600g',
       'High Jump' : 'High Jump',
       'Pole Vault' : 'Pole Vault',
       'Long Jump' : 'Long Jump',
       'Triple Jump' : 'Triple Jump',
       'Hammer' : 'Hammer',
       'Triathlon - standard' : 'Triathlon - standard',
       'Pentathlon (outdoor)- Standard' : 'Pentathlon (outdoor)- Standard',
       'Decathlon - Standard' : 'Decathlon - Standard'
    }
    athlete_class = models.CharField(max_length=50, choices=CLASS, default="select class")
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
       