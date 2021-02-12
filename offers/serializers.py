from rest_framework import serializers
from .models import OfferModel


class OfferSerializer(serializers.ModelSerializer):
         
     class Meta:
        model = OfferModel
        fields = (
            'partner_id',
            'partner_name',
            'value',
            'installments',
            'tax_rate_percent_montly',
            'total_value'
        )