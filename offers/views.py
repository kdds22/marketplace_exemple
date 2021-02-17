from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import OfferModel
from .serializers import OfferSerializer
from helpers.offer_service import OfferService

# Create your views here.
class OffersListView(generics.ListCreateAPIView):
    permission_classes = [AllowAny]
    queryset = OfferModel.objects.all()
    serializer_class = OfferSerializer
    
    def post(self, request, *args, **kwargs):
        offers = OfferService().search_offers(client_data=self.request.data)
        return Response({"Offers": offers.serialized})
    
    def get(self, request, *args, **kwargs):
        offers = OfferService().search_offers_by_client(client_data=self.request.data, client_modifiable=False)
        if offers != None:
            return Response({"Last Offers by Client": offers.serialized})
        else:
            return Response({"message":"Client isn't available"})