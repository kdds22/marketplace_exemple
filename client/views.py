from rest_framework import generics
from .models import ClientModel
from .serializers import ClientSerializer
from rest_framework.permissions import AllowAny

# Create your views here.
class ClientListView(generics.ListCreateAPIView):
    permission_classes = [AllowAny]
    queryset = ClientModel.objects.all()
    serializer_class = ClientSerializer