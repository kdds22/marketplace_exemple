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
    
    
    def create(self, validated_data):
        client, _ = self.Meta.model.objects.get_or_create(**validated_data)
        return client