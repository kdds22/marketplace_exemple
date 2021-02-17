# Estrutura e Fluxo da solução

### Criar os modelos das entidades do projeto

- CLIENTE:

    NAME | TYPE | EXTRAS
    ---- | ---- | ------
    cpf | string | max:14
    name | string | max:255
    born_date | date  | 
    email | string | max:255
    phone | string | max:20
    monthly_income | decimal | max:8(2)

- OFERTA:

    NAME | TYPE | EXTRAS
    ---- | ---- | ------
    partner_id | int | 
    partner_name | string | max:150
    value | decinal | max:8(2)
    installments | int | 
    tax_rate_percent_montly | decimal | max:3(2)
    total_value | decimal | max:8(2)
    history_offers | ForeignKey(OFERTA_HISTORICO) | 

- OFERTA_HISTORICO:
*** Regra do projeto: endpoint tem validade de 10 min por cliente

    NAME | TYPE | EXTRAS
    ---- | ---- | ------
	last_call | datetime | 
	client | ForeignKey(CLIENTE) | 

- PROPOSTA:
*** Regra do Projeto: um cliente só poderá enviar uma proposta (com a mesma oferta) a cada 30 dias 

    NAME | TYPE | EXTRAS
    ---- | ---- | ------
	client | ForeignKey(CLIENT) | 
	offer | ForeignKey(OFERTA) | 
	last_send | date | 
	proposal_id | int | 
	message | string | max:200


### Criar serializadores pra conversão de dados (BancoDeDados <-> aplicação)

- CLIENTE:
  - importar campos do modelo(CLIENTE) e serializar:
    ```python
    class ClientSerializer(serializers.ModelSerializer):
        
        class Meta:
            model = ClientModel
            fields = (
                'cpf',
                'name',
                'born_date',
                'email',
                'phone',
                'monthly_income'
        )
        
        # Usado pra criar um cliente (caso não exista) ou 'pegar' as informações de um cliente existente
        def create(self, validated_data):
            client, _ = self.Meta.model.objects.get_or_create(**validated_data)
            return client
    ```

- OFERTA:
  - importar campos do modelo(OFERTA)
  ```python
  class OfferSerializer(serializers.ModelSerializer):
         
     class Meta:
        model = OfferModel
        fields = (
            'partner_id',
            'partner_name',
            'value',
            'installments',
            'tax_rate_percent_montly',
            'total_value'
        )
    ```

- PROPOSTA:
  - importar campos do modelo(PROPOSTA)
    ```python
    class ProposalSerializer(serializers.ModelSerializer):
         
        class Meta:
            model = ProposalModel
            fields = (
                'client',
                'offer',
                'last_send',
                'proposal_id',
                'message'
            )
    ```


### Criar as Views pra receber os dados passados

- OFERTA:
    - importar serializador
        ```python
        import OfferSerializer
        ```
    - pegar dados da requisicao
        ```python
        offers = OfferService().search_offers(client_data=self.request.data)
        ```
- PRPOSTA:
    - importar serializador
        ```python
        import ProposalSerializer
        ```
    - pegar dados da requisicao
        ```python
        proposals = ProposalService().send_proposal(proposal_data=self.request.data)
        ```
        - Dados do Cliente
            ```python
            proposal_data['client']
            ```
        - Dados da Proposta
            ```python
            proposal_data['offer']
            ```


### Criar Urls pra indicar onde será feita a requisicao
	
- CLIENTE:
    ```python
    url(r'^clients/$', views.ClientListView.as_view(), name='clients-list'),
    ```
- OFERTA:
    ```python
    url(r'^offers/$', views.OffersListView.as_view(), name='offers-list'),
    ```
- PROPOSTA:
    ```python
    url(r'^proposals/$', views.ProposalsListView.as_view(), name='proposals-list'),
    ```

## Criar Helpers pra realizar processamentos dos dados
1. OFERTA:
    1. validar clientes
        ```python
            def instance_client(self, client: dict):
                
                #serializa os dados no modelo existente do cliente
                serial = ClientSerializer(data=client) 

                #verifica se a serialização dos dados são válidas antes de salvar
                serial.is_valid() 
                
                return serial.save() 
        ```

    2. validar ofertas
        ```python
        OfferService.filter_offer(self, proposal_data, history_offers_id)
        ```

    3. gravar ofertas requisitas pelo cliente
        ```python
        def save(self, offers_data: dict, client_instance: object):
        
            # cria um historico de solicitação do cliente
            instance_offer_history = HistoryOfferModel.objects.create(client=client_instance) 
            
            for offers in offers_data:

                # serializa os dados no modelo existente da oferta
                serial = OfferSerializer(data=offers)
                try:

                    #verifica se a serialização dos dados são válidas antes de salvar
                    serial.is_valid()

                    # armazena os dados junto ao historico de solicitação do clientes
                    # servirá tambem como base para impedir novas solicitações de ofertas dentro de 10 minutos
                    serial.save(history_offers=instance_offer_history)
                
                except ...
        ```

    4. pesquisar ofertas existentes ou solicitar novas ofertas
        ```python

        # verificar se há ofertas vinculadas a um historico do cliente
        self.query_db = self.filter_history_offer(client_data,False)
        
        # caso exista oferta...
        if self.query_db.exists(): 

            # serializa os dados da oferta
            serial = OfferSerializer(self.query_db, many=True) 
            self.serialized = serial.data
            
            # retorna as ofertas para a requisição
            return self 

        # caso NÃO exista oferta...solicita novas...
        else:
            # nova requisição de ofertas (api ficticia)
            new_offers_list = requests.post('https://xyz/offers', json=client_data)

            # decodifica o text para objeto json
            new_offers_list_decoded = json.loads(new_offers_list.text)
            offers = new_offers_list_decoded['offers']

            # armazenas novo historico do cliente junto as novas ofertas
            self.save(offers_data=offers, client_instance=self.instance_client)

            # retorna uma nova requisição, agora com os novos dados e devolvidos como resposta
            return self.search(client_data=client_data, client_modifiable=False)
        ```

2. PROPOSTA:
    1. validar ofertas
        ```python
        OfferService.filter_offer(self, proposal_data, history_offers_id)
        ```

    2. validar clientes
        ```python
        ClientService.filter_client(self, proposal_data['client'])
        ```

    3. verificar se o cliente enviou a mesma proposta em menos de 30 dias
        ```python
        def if_proposal_exist(self):

            # verifica na base, se há alguma proposta com o ID do cliente e o ID da oferta
            self.query_db_proposal = self.filter_proposal(self.query_db_client.values()[0]['id'],self.query_db_offer.values()[0]['id'])
            
            # caso exista proposta...
            if self.query_db_proposal.exists():

                # valida se a proposta existente tem menos de 30 dias criada
                if ((self.query_db_proposal.values()[0]['last_send'] + timedelta(days=30)) < datetime.now().date()):
                    # cria nova proposta
                else:
                    # retorna mensagem informando q a mesma proposta esta sendo analisada
            
            # caso NÃO exista proposta...
            else:
                # cria nova proposta
        ```

    4. gravar e enviar proposta
        - Caso seja nova ou +30 dias
            ```python
            def create_proposal(self, offer_data, client_data):

                # nova requisição de proposta (api ficticia)
                new_proposal = requests.post('https://xyz/proposal/')

                # decodifica o text para objeto json
                new_proposal_decoded = json.loads(new_proposal.text)

                # api retorna 2 campos (ID da proposta e uma Mensagem)
                proposal_id = new_proposal_decoded['proposal_id']
                message = new_proposal_decoded['message']

                # Dados da proposta serão armazenados na base...
                # junto aos dados do cliente e da oferta escolhida
                self.save(proposal_id_data=proposal_id, proposal_message=message, offer_data=offer_data, client_data=client_data)
                
                return {"message":"Proposta enviada com sucesso."}
            ```

# Utilizando API

- start server:
    - python3 manage.py runserver

- [GET,POST] http://127.0.0.1:8000/clients/

    ```json
    {
        "cpf":"11122233300",
        "name":"Fulano Beltrano do Sicrano",
        "born_date":"1901-01-01",
        "email":"fulaninho@email.com",
        "phone":"+55099912345678",
        "monthly_income":999999.00
    }
    ```
- [GET,POST] http://127.0.0.1:8000/offers/
    - GET_BODY:
        
        ```json
        {
            "cpf":"11122233300",
            "name":"Fulano Beltrano do Sicrano",
            "born_date":"1901-01-01",
            "email":"fulaninho@email.com",
            "phone":"+55099912345678",
            "monthly_income":999999.00
        }
        ```
    - GET_RESPONSE <offers_list>:

        ```json
        {
            "Last Offers by Client": [
                {
                    "partner_id": 1,
                    "partner_name": "Parceiro 1",
                    "value": "10000.00",
                    "installments": 24,
                    "tax_rate_percent_montly": 2.0,
                    "total_value": "12689.04"
                }
            ]
        }
        ```

    - POST_BODY:

        ```json
        {
            "cpf":"11122233300",
            "name":"Fulano Beltrano do Sicrano",
            "born_date":"1901-01-01",
            "email":"fulaninho@email.com",
            "phone":"+55099912345678",
            "monthly_income":999999.00
        }
        ```
    
    - POST_RESPONSE:

        ```json
        {
            "Offers": [
                {
                    "partner_id": 1,
                    "partner_name": "Parceiro 1",
                    "value": "10000.00",
                    "installments": 24,
                    "tax_rate_percent_montly": 2.0,
                    "total_value": "12689.04"
                }
            ]
        }
        ```
    
- [GET,POST] http://127.0.0.1:8000/proposals/
    
    - GET_RESPONSE:

    ```json
    [
        {
            "client": 2,
            "offer": 30,
            "last_send": "2021-01-05",
            "proposal_id": 552,
            "message": "Proposta criada com sucesso"
        }
    ]
    ```

    - POST_BODY:

    ```json
    {
        "client":{
            "cpf":"11122233300",
            "name":"Fulano Beltrano do Sicrano",
            "born_date":"1901-01-01",
            "email":"fulaninho@email.com",
            "phone":"+55099912345678",
            "monthly_income":999999.00
        },
        "offer":{
            "partner_id": 1,
            "partner_name": "Parceiro 1",
            "value": "10000.00",
            "installments": 24,
            "tax_rate_percent_montly": 2.0,
            "total_value": "12689.04"
        }
    }
    ```

    - POST_RESPONSE:

    ```json
    {"message":"Proposta enviada com sucesso."}
    ```

    - POST_RESPONSE_ERRORS:

    ```json
    {"message":"Já existe uma proposta para esses dados. E será analisada dentro de 30 dias desde seu envio."},
    {"message":"Oferta enviada não coincide com a base de dados"},
    {"message":"Ainda não há ofertas válidas para o cliente informado."},
    {"message":"O cliente informado é invalido."},
    {"message":"Não foi informado um cliente."},
    {"message":"Não foi informado uma oferta."},
    {"detail": "JSON parse error - Extra data: line X column Y (char Z)"},
    {"message":str(e)}
    ```