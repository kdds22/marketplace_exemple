from django.db import models
import datetime
from client.models import ClientModel


class HistoryOfferModel(models.Model):
    last_call = models.DateField(blank=True, null=False)
    client = models.ForeignKey(ClientModel, on_delete=models.PROTECT, related_name='client_history_offer', blank=False, null=False)

    class Meta:
        db_table = 'history_offers'
    
    def save(self, *args, **kwargs):
        self.last_call = datetime.now() + datetime.timedelta(minutes=10)
        super(HistoryOfferModel, self).save(*args, **kwargs)


# Create your models here.
class OfferModel(models.Model):
    partner_id = models.IntegerField(blank=True, null=False)
    partner_name = models.CharField(max_length=150, blank=True, null=False)
    value = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=False)
    installments = models.IntegerField(blank=True, null=False)
    tax_rate_percent_montly = models.FloatField(blank=True, null=False)
    total_value = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=False)
    history_offers = models.ForeignKey(HistoryOfferModel, on_delete=models.CASCADE, related_name='history_offers_fk', blank=False, null=True)
    
    class Meta:
        db_table = 'offers'
