from datetime import datetime, date

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


    def client(self, client: dict):
        serial = ClientSerializer(data=client)
        serial.is_valid()
        return serial.save()
    

    def save(self, proposal_id_data: str, proposal_message: str, offer_data: dict, client_data: dict):
        #print(proposal_id_data,proposal_message,offer_data.values())
        # print("Dados do cliente:",client_data)
        
        instance_offer = OfferModel.objects.filter(
            history_offers__id=offer_data["history_offers_id"], 
            id=offer_data["id"])
        
        instance_client = ClientModel.objects.filter(
            id=client_data["id"]
        )
        
        #print(instance_offer_history.values())
        proposal = {
            "client":client_data["id"],
            "offer":offer_data["id"],
            "last_send":datetime.now().date(),
            "proposal_id":proposal_id_data,
            "message":proposal_message
        }
        
        # print(proposal)
        
        serial = ProposalSerializer(data=proposal)
        print(serial)
        try:
            serial.is_valid()
            if serial.is_valid():
                print('É valido')
                serial.save()
            else:
                print("NÃO é valido",serial.errors)
        except Exception as e:
            print("error: ",e)
        
        # for offers in offers_data:
        #     serial = OfferSerializer(data=offers)
        #     try:
        #         serial.is_valid()
        #         serial.save(history_offers=instance_offer_history)
        #     except Exception as e:
        #         logging.error(f'In OffersListView view: {e}'.encode('utf-8'))


    def search_client(self, proposal_data):        
        self.query_db_client = ClientModel.objects.filter(
            cpf=proposal_data['client']['cpf'],
            name=proposal_data['client']['name'],
            born_date=proposal_data['client']['born_date'],
            email=proposal_data['client']['email'],
            phone=proposal_data['client']['phone'],
            monthly_income=proposal_data['client']['monthly_income']
        )
        
        print("Cliente:",self.query_db_client.values())
        
        
        if self.query_db_client.exists():
            self.query_db = OfferModel.objects.filter(
            history_offers__last_call__lt=datetime.now(),
            history_offers__client__cpf=proposal_data['client']['cpf'],
            history_offers__client__name=proposal_data['client']['name'],
            history_offers__client__born_date=proposal_data['client']['born_date'],
            history_offers__client__email=proposal_data['client']['email'],
            history_offers__client__phone=proposal_data['client']['phone'],
            history_offers__client__monthly_income=proposal_data['client']['monthly_income']
            ).annotate(offers_count=Count('history_offers')).order_by('-offers_count')[5:]
            
            print("history: ",self.query_db.values())
            
            if self.query_db.exists():
                self.query_db_offer = OfferModel.objects.filter(
                    partner_id=proposal_data['offer']['partner_id'],
                    partner_name=proposal_data['offer']['partner_name'],
                    value=proposal_data['offer']['value'],
                    installments=proposal_data['offer']['installments'],
                    tax_rate_percent_montly=proposal_data['offer']['tax_rate_percent_montly'],
                    total_value=proposal_data['offer']['total_value'],
                    history_offers__id=self.query_db.values()[0]['history_offers_id']
                )
                print("Oferta: ",  self.query_db_offer.values())
                if self.query_db_offer.exists():
                    #print(self.query_db_client.values()[0]['cpf'])
                    #print(self.query_db.values())
                    #print(self.query_db_offer.values()[0])
                    print("oferta existe")
                    
                    new_proposal = requests.post('https://fb254f08-fd54-4731-b4d7-90149503e6c5.mock.pstmn.io/proposal/')
                    new_proposal_decoded = json.loads(new_proposal.text)
                    proposal_id = new_proposal_decoded['proposal_id']
                    message = new_proposal_decoded['message']
                    self.save(proposal_id_data=proposal_id, proposal_message=message, offer_data=self.query_db_offer.values()[0], client_data=self.query_db_client.values()[0])
                    return {"message":"Proposta enviada com sucesso."}
                else:
                    return {"message":"Oferta enviada não coincide com a base de dados"}
            else:
                #oferta invalida para o cliente
                print("historico invalido para o cliente")
                print(self.query_db_client.values())
                print(self.query_db)
                return {"message":"Ainda não há ofertas válidas para o cliente informado."}
        else:
            print(self.query_db_client)
            return {"message":"O cliente informado é invalido."}
        
