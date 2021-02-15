from datetime import datetime, date, timedelta

import requests
import json
import logging

from offers.models import OfferModel
from client.models import ClientModel
from proposals.models import ProposalModel
from client.serializers import ClientSerializer
from .client_service import ClientService
from .offer_service import OfferService
from proposals.serializers import ProposalSerializer

from django.db.models import Count


class ProposalService(object):
    def __init__(self):
        self.query_db = object()
        self.query_db_client = object()
        self.query_db_offer = object()
        self.query_db_proposal = object()

    def save(self, proposal_id_data: str, proposal_message: str, offer_data: dict, client_data: dict):

        proposal = {
            "client":client_data["id"],
            "offer":offer_data["id"],
            "last_send":datetime.now().date(),
            "proposal_id":proposal_id_data,
            "message":proposal_message
        }
        
        serial = ProposalSerializer(data=proposal)
        try:
            serial.is_valid()
            serial.save()
        except Exception as e:
            logging.error(f'In ProposalsListView view: {e}'.encode('utf-8'))


    def create_proposal(self, offer_data, client_data):
        new_proposal = requests.post('https://fb254f08-fd54-4731-b4d7-90149503e6c5.mock.pstmn.io/proposal/')
        new_proposal_decoded = json.loads(new_proposal.text)
        proposal_id = new_proposal_decoded['proposal_id']
        message = new_proposal_decoded['message']
        self.save(proposal_id_data=proposal_id, proposal_message=message, offer_data=offer_data, client_data=client_data)
        return {"message":"Proposta enviada com sucesso."}
    
    def filter_proposal(self,client_id,offer_id):
        return ProposalModel.objects.filter(
            client_id=client_id,
            offer_id=offer_id
        ).order_by('-last_send')[:1]

    def if_proposal_exist(self):
        self.query_db_proposal = self.filter_proposal(self.query_db_client.values()[0]['id'],self.query_db_offer.values()[0]['id'])
        
        if self.query_db_proposal.exists():
            if ((self.query_db_proposal.values()[0]['last_send'] + timedelta(days=30)) < datetime.now().date()):
                return self.create_proposal(self.query_db_offer.values()[0],self.query_db_client.values()[0])
            else:
                return {"message":"Já existe uma proposta para esses dados. E será analisada dentro de 30 dias desde seu envio."}    
        else:
            return self.create_proposal(self.query_db_offer.values()[0],self.query_db_client.values()[0])
            

    def if_offer_exist(self, proposal_data):
        self.query_db_offer = OfferService.filter_offer(self, proposal_data,self.query_db.values()[0]['history_offers_id'])
        
        if self.query_db_offer.exists():
            return self.if_proposal_exist()
        
        else:
            return {"message":"Oferta enviada não coincide com a base de dados"}
    
    def search_client(self, proposal_data):        
        self.query_db_client = ClientService.filter_client(self, proposal_data['client'])
        
        if self.query_db_client.exists():
            self.query_db = OfferService.filter_history_offer(self,proposal_data['client'],True)
            
            if self.query_db.exists():
                return self.if_offer_exist(proposal_data)
            
            else:
                return {"message":"Ainda não há ofertas válidas para o cliente informado."}
        else:
            return {"message":"O cliente informado é invalido."}
    
    
