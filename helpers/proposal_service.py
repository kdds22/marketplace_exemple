from datetime import datetime, date, timedelta

import requests
import json
import logging

from offers.models import HistoryOfferModel, OfferModel
from client.models import ClientModel
from proposals.models import ProposalModel
from offers.serializers import OfferSerializer
from client.serializers import ClientSerializer
from proposals.serializers import ProposalSerializer

from .offer_service import OfferService

from django.db.models import Count


class ProposalService(object):
    def __init__(self):
        self.query_db = object()
        self.query_db_client = object()
        self.query_db_offer = object()
        self.query_db_proposal = object()


    def client(self, client: dict):
        serial = ClientSerializer(data=client)
        serial.is_valid()
        return serial.save()
    

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


    def filter_client(self, proposal_data):
        return ClientModel.objects.filter(
            cpf=proposal_data['client']['cpf'],
            name=proposal_data['client']['name'],
            born_date=proposal_data['client']['born_date'],
            email=proposal_data['client']['email'],
            phone=proposal_data['client']['phone'],
            monthly_income=proposal_data['client']['monthly_income']
        )
    
    def filter_history_offer(self,proposal_data):
        return OfferModel.objects.filter(
            history_offers__last_call__lt=datetime.now(),
            history_offers__client__cpf=proposal_data['client']['cpf'],
            history_offers__client__name=proposal_data['client']['name'],
            history_offers__client__born_date=proposal_data['client']['born_date'],
            history_offers__client__email=proposal_data['client']['email'],
            history_offers__client__phone=proposal_data['client']['phone'],
            history_offers__client__monthly_income=proposal_data['client']['monthly_income']
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
    
    def filter_proposal(self,client_id,offer_id):
        return ProposalModel.objects.filter(
            client_id=client_id,
            offer_id=offer_id
        ).order_by('-last_send')[:1]

    def if_proposal_exist(self):
        if self.query_db_proposal.exists():
            if ((self.query_db_proposal.values()[0]['last_send'] + timedelta(days=30)) < datetime.now().date()):
                return self.create_proposal(self.query_db_offer.values()[0],self.query_db_client.values()[0])
            else:
                return {"message":"Já existe uma proposta para esses dados. E será analisada dentro de 30 dias desde seu envio."}    
        else:
            return self.create_proposal(self.query_db_offer.values()[0],self.query_db_client.values()[0])
            

    def if_offer_exist(self):
        if self.query_db_offer.exists():
                        
            self.query_db_proposal = self.filter_proposal(self.query_db_client.values()[0]['id'],self.query_db_offer.values()[0]['id'])
                
            return self.if_proposal_exist()
            
            
        else:
            return {"message":"Oferta enviada não coincide com a base de dados"}
    
    def search_client(self, proposal_data):        
        self.query_db_client = self.filter_client(proposal_data)
        
        if self.query_db_client.exists():
            self.query_db = self.filter_history_offer(proposal_data)
            
            if self.query_db.exists():
                self.query_db_offer = self.filter_offer(proposal_data,self.query_db.values()[0]['history_offers_id'])
                
                return self.if_offer_exist()
                
            else:
                return {"message":"Ainda não há ofertas válidas para o cliente informado."}
        else:
            return {"message":"O cliente informado é invalido."}
    
    
