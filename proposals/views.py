from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import ProposalModel
from .serializers import ProposalSerializer
from helpers.proposal_service import ProposalService

# Create your views here.
class ProposalsListView(generics.ListCreateAPIView):
    permission_classes = [AllowAny]
    queryset = ProposalModel.objects.all()
    serializer_class = ProposalSerializer
    
    def post(self, request, *args, **kwargs):
        proposals = ProposalService().send_proposal(proposal_data=self.request.data)
        if proposals != None:
            return Response({"Last Proposals by Client": proposals["message"]})
        else:
            return Response({"Error: Proposal isn't available"})