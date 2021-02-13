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
    installments | nt | 
    tax_rate_percent_montly | decimal | max:3(2)
    total_value | decimal | max:8(2)
    history_offers | ForeignKey(OFERTA_HISTORICO) | 

- OFERTA_HISTORICO:
*** Regra do projeto: endpoint tem validade de 10 min por cliente

    NAME | TYPE | EXTRAS
    ---- | ---- | ------
	last_call | date | 
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
  - importar campos do modelo(CLIENTE)
- OFERTA:
  - importar campos do modelo(OFERTA)
- PROPOSTA:
  - importar campos do modelo(PROPOSTA)

### Criar as Views pra receber os dados passados

- CLIENTE:
    - importar serializador
    - pegar dados da requisicao
- OFERTA:
    - importar serializador
    - pegar dados da requisicao
        - Dados do Cliente
- PRPOSTA:
    - importar serializador
    - pegar dados da requisicao
        - Dados do Cliente
        - Dados da Proposta


### Criar Urls pra indicar onde será feita a requisicao
	
- CLIENTE:
    - url_client
- OFERTA:
    - url_offer
- PROPOSTA:
    - url_proposal

## Criar Helpers pra realizar processamentos dos dados
1. OFERTA:
    1. validar clientes
    2. validar ofertas
    3. gravar ofertas requisitas pelo cliente
    4. pesquisar ofertas existentes ou consultar novas ofertas
2. PROPOSTA:
    1. validar ofertas
    2. validar clientes
    3. verificar se o cliente enviou a mesma proposta em menos de 30 dias
    4. gravar proposta
        1. caso seja nova
        2. +30 dias
    5. enviar proposta