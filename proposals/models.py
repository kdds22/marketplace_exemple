from django.db import models
from client.models import ClientModel
from offers.models import OfferModel

# Create your models here.
class ProposalModel(models.Model):
    client = models.ForeignKey(ClientModel, on_delete=models.PROTECT, related_name='proposal_client', blank=False, null=False)
    offer = models.ForeignKey(OfferModel, on_delete=models.PROTECT, related_name='proposal_offer', blank=False, null=False)
    last_send = models.DateField(blank=False, null=False)
    proposal_id = models.PositiveIntegerField(blank=True, null=False)
    message = models.CharField(max_length=200, blank=True, null=False)
    
    class Meta:
        db_table = 'proposal'