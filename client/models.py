from django.db import models

# Create your models here.
class ClientModel(models.Model):
    cpf = models.CharField(max_length=14,blank=True, null=False)
    name = models.CharField(max_length=255, blank=True, null=False)
    born_date = models.DateField(blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=False)
    monthly_income = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=False)
    
    class Meta:
        db_table = 'client'