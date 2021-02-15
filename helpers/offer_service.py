from datetime import datetime

import requests
import json
import logging

from offers.models import HistoryOfferModel, OfferModel
from client.models import ClientModel
from offers.serializers import OfferSerializer
from client.serializers import ClientSerializer
from django.db.models import Count


class OfferService(object):
    def __init__(self):
        self.query_db = object()
        self.query_db_client = object()


    def client(self, client: dict):
        serial = ClientSerializer(data=client)
        serial.is_valid()
        return serial.save()
    

    def save(self, offers_data: dict, client_instance: object):
        
        instance_offer_history = HistoryOfferModel.objects.create(client=client_instance)
        
        for offers in offers_data:
            serial = OfferSerializer(data=offers)
            try:
                serial.is_valid()
                serial.save(history_offers=instance_offer_history)
            except Exception as e:
                logging.error(f'In OffersListView view: {e}'.encode('utf-8'))

    def search(self, client_data, client_modifiable=True):
        self.instance_client = self.client(client=client_data)
        
        self.query_db = OfferModel.objects.filter(
            history_offers__last_call__gt=datetime.now(),
            history_offers__client__cpf=client_data['cpf'],
            history_offers__client__name=client_data['name'],
            history_offers__client__born_date=client_data['born_date'],
            history_offers__client__email=client_data['email'],
            history_offers__client__phone=client_data['phone'],
            history_offers__client__monthly_income=client_data['monthly_income']
            
        )
        
        if self.query_db.exists():
            serial = OfferSerializer(self.query_db, many=True)
            self.serialized = serial.data
            return self
        else:
            new_offers_list = requests.post('https://fb254f08-fd54-4731-b4d7-90149503e6c5.mock.pstmn.io/offers', json=client_data)
            new_offers_list_decoded = json.loads(new_offers_list.text)
            offers = new_offers_list_decoded['offers']
            self.save(offers_data=offers, client_instance=self.instance_client)
            return self.search(client_data=client_data, client_modifiable=False)
        
        
    def search_client(self, client_data, client_modifiable=True):        
        self.query_db_client = ClientModel.objects.filter(
            cpf=client_data['cpf'],
            name=client_data['name'],
            born_date=client_data['born_date'],
            email=client_data['email'],
            phone=client_data['phone'],
            monthly_income=client_data['monthly_income']
        )
        
        if self.query_db_client.exists():
            
            self.query_db = OfferModel.objects.filter(
            history_offers__last_call__lte=datetime.now(),
            history_offers__client__cpf=client_data['cpf'],
            history_offers__client__name=client_data['name'],
            history_offers__client__born_date=client_data['born_date'],
            history_offers__client__email=client_data['email'],
            history_offers__client__phone=client_data['phone'],
            history_offers__client__monthly_income=client_data['monthly_income']
            ).annotate(offers_count=Count('history_offers')).order_by('-offers_count')[5:]
            
            if self.query_db.exists():
                serial = OfferSerializer(self.query_db, many=True)
                self.serialized = serial.data
                return self
            else:
                return None
        else:
            return None
