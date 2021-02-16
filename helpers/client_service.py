from client.models import ClientModel
from client.serializers import ClientSerializer

class ClientService(object):
    def __init__(self):
        self.possible_query = object()


    def instance_client(self, client: dict):
        serial = ClientSerializer(data=client)
        serial.is_valid()
        return serial.save()
    

    def filter_client(self, client_data):
        return ClientModel.objects.filter(
            cpf=client_data['cpf'],
            name=client_data['name'],
            born_date=client_data['born_date'],
            email=client_data['email'],
            phone=client_data['phone'],
            monthly_income=client_data['monthly_income']
        )
