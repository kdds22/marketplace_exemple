from rest_framework import serializers
from .models import ProposalModel


class ProposalSerializer(serializers.ModelSerializer):
         
     class Meta:
        model = ProposalModel
        fields = (
            'client',
            'offer',
            'last_send',
            'proposal_id',
            'message'
        )
