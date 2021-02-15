from datetime import datetime

import requests
import json
import logging

from offers.models import HistoryOfferModel, OfferModel
from client.models import ClientModel
from offers.serializers import OfferSerializer
from client.serializers import ClientSerializer
from .client_service import ClientService
from django.db.models import Count


class OfferService(object):
    def __init__(self):
        self.query_db = object()
        self.query_db_client = object()
    

    def save(self, offers_data: dict, client_instance: object):
        
        instance_offer_history = HistoryOfferModel.objects.create(client=client_instance)
        
        for offers in offers_data:
            serial = OfferSerializer(data=offers)
            try:
                serial.is_valid()
                serial.save(history_offers=instance_offer_history)
            except Exception as e:
                logging.error(f'In OffersListView view: {e}'.encode('utf-8'))

    def filter_history_offer(self,client_data, annotate: bool):
        if not annotate:
            return OfferModel.objects.filter(
                history_offers__last_call__gt=datetime.now(),
                history_offers__client__cpf=client_data['cpf'],
                history_offers__client__name=client_data['name'],
                history_offers__client__born_date=client_data['born_date'],
                history_offers__client__email=client_data['email'],
                history_offers__client__phone=client_data['phone'],
                history_offers__client__monthly_income=client_data['monthly_income']
            )
        else:
            return OfferModel.objects.filter(
            history_offers__last_call__lte=datetime.now(),
            history_offers__client__cpf=client_data['cpf'],
            history_offers__client__name=client_data['name'],
            history_offers__client__born_date=client_data['born_date'],
            history_offers__client__email=client_data['email'],
            history_offers__client__phone=client_data['phone'],
            history_offers__client__monthly_income=client_data['monthly_income']
            ).annotate(offers_count=Count('history_offers')).order_by('-offers_count')[5:]

    def filter_offer(self, proposal_data, history_offers_id):
        return OfferModel.objects.filter(
            partner_id=proposal_data['offer']['partner_id'],
            partner_name=proposal_data['offer']['partner_name'],
            value=proposal_data['offer']['value'],
            installments=proposal_data['offer']['installments'],
            tax_rate_percent_montly=proposal_data['offer']['tax_rate_percent_montly'],
            total_value=proposal_data['offer']['total_value'],
            history_offers__id=history_offers_id
        )

    def search(self, client_data, client_modifiable=True):
        self.instance_client = ClientService.instance_client(self, client=client_data)
        
        self.query_db = self.filter_history_offer(client_data,False)
        
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
        self.query_db_client = ClientService.filter_client(self, client_data=client_data)
        
        if self.query_db_client.exists():
            
            self.query_db = self.filter_history_offer(client_data,True)
            
            if self.query_db.exists():
                serial = OfferSerializer(self.query_db, many=True)
                self.serialized = serial.data
                return self
            else:
                return None
        else:
            return None
