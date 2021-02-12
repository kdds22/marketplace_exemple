from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import OfferModel
from .serializers import OfferSerializer
from helpers.offer_service import OfferService

# Create your views here.
class OffersListView(generics.ListCreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = OfferSerializer
    
    def post(self, request, *args, **kwargs):
        offers = OfferService().search(client_data=self.request.data)
        return Response({"Offers": offers.serialized})