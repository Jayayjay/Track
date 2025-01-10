from django.db import models

# Create your models here.
class ContactMessage(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField()
    subject = models.CharField(max_length=50)
    message = models.TextField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Contact Information"
    
    def __str__(self):
        return f"{self.name} - {self.subject}"