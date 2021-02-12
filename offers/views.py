from rest_framework import generics
from .models import OfferModel
from .serializers import OfferSerializer

# Create your views here.
class OffersListView(generics.ListCreateAPIView):
    queryset = OfferModel.objects.all()
    serializer_class = OfferSerializer