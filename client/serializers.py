from rest_framework import serializers
from .models import ClientModel


class ClientSerializer(serializers.ModelSerializer):
         
     class Meta:
        model = ClientModel
        fields = (
            'cpf',
            'name',
            'born_date',
            'email',
            'phone',
            'monthly_income'
        )