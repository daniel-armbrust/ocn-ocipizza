# OCI Pizza - Instruções do delivery-service

Estas instruções complementam `services/AGENTS.md` e se aplicam somente ao
`delivery-service`. Em caso de conflito, estas regras específicas têm prioridade.

## Responsabilidade

O `delivery-service` é responsável pelas áreas atendidas pela pizzaria e pela
cotação de entrega. Ele informa se um CEP está dentro de uma área ativa e
retorna a taxa e o prazo estimado correspondentes.

O serviço não deve acessar dados de pedidos, usuários ou pizzas diretamente.
Quando precisar dessas informações, deve utilizar contratos de API ou eventos
definidos pela aplicação.

## Persistência

- O provider atualmente implementado é o Oracle NoSQL.
- A seleção do provider deve ocorrer pela configuração existente, sem criar
  conexões diretamente nas rotas ou nos serviços.
- O acesso aos dados deve ser feito por `repositories/` e pela injeção de
  dependências definida em `dependencies/database.py`.
- Em desenvolvimento, o Oracle NoSQL local deve ser preparado pelo
  `bootstrap.sh`. O bootstrap pode recriar a tabela e remover os dados locais;
  não o execute contra dados que precisem ser preservados.
- Não adicione um provider alternativo sem implementar seu repositório,
  unidade de trabalho, configuração e documentação correspondente.

## Organização do código

- `routes/`: recebe requisições, valida parâmetros, chama o serviço e monta a
  resposta JSend.
- `services/`: concentra regras de normalização de CEP, consulta de faixas e
  operações CRUD das áreas.
- `repositories/`: encapsula a persistência das áreas de entrega.
- `schemas/`: define os contratos de entrada e saída da API.
- `models/`: representa o modelo interno de uma área de entrega.
- `dependencies/`: fornece autenticação, persistência e demais dependências
  compartilhadas.

As rotas não devem conter regras de negócio nem acessar o repositório
diretamente.

## Rotas e autorização

- `GET /delivery/quote/{zip_code}` é a operação de cotação para usuários
  autenticados.
- As rotas `/admin/delivery/areas` e suas operações filhas são administrativas
  e exigem um access token JWT com `is_admin=true`.
- O serviço utiliza `user-service` somente para obter as chaves públicas JWKS;
  não consulta o banco de dados de usuários.
- A claim `is_kitchen` não concede acesso às operações administrativas de áreas
  de entrega.
- Erros de autenticação e autorização devem preservar os códigos HTTP e o
  padrão JSend definidos pelo serviço.

## Contratos e respostas

- As respostas da API devem permanecer no padrão JSend.
- A taxa de entrega deve ser serializada como valor monetário, sem expor um
  objeto `Decimal` que não possa ser convertido para JSON.
- O CEP deve ser normalizado antes da consulta, e somente áreas `active=true`
  podem participar da cotação.
- Alterações em endpoints, filtros, campos ou códigos de erro devem ser
  refletidas no `README.md` do serviço.

## Segurança e qualidade

- Não exponha detalhes internos de persistência ou autenticação nas respostas.
- Não adicione segredos, tokens ou credenciais ao código ou à documentação.
- Não crie diretórios ou arquivos de testes sem solicitação explícita.
- Preserve testes existentes, caso sejam adicionados posteriormente, e execute
  apenas as validações pertinentes à alteração realizada.
