from rest_framework import generics
from .models import ClientModel
from .serializers import ClientSerializer

# Create your views here.
class ClientListView(generics.ListCreateAPIView):
    queryset = ClientModel.objects.all()
    serializer_class = ClientSerializer