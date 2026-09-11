# Pizza Service Specification

## 1. Objetivo

O `pizza-service` é responsável pelo domínio de catálogo de pizzas da aplicação OCI Pizza.

O serviço deve permitir que usuários e outros serviços da aplicação consultem e gerenciem informações relacionadas ao catálogo de pizzas.

O `pizza-service` é a fonte de verdade para as informações do catálogo.

## 2. Escopo

O `pizza-service` deve permitir:

- Consultar pizzas do catálogo
- Consultar detalhes de uma pizza
- Cadastrar novas pizzas
- Atualizar informações de pizzas
- Remover pizzas
- Gerenciar categorias
- Controlar disponibilidade dos produtos

O `pizza-service` NÃO é responsável por:

- Autenticação de usuários
- Gerenciamento de identidade
- Gerenciamento de usuários
- Criação e gerenciamento de pedidos
- Processamento de pagamentos
- Envio de notificações
- Interface gráfica da aplicação

## 3. Conceitos do Domínio

Uma pizza representa um produto disponível no catálogo da aplicação OCI Pizza.

Uma pizza possui informações necessárias para apresentação ao usuário e utilização pelos demais serviços.

A entidade Pizza possui os seguintes campos:

| Campo       | Descrição                                             |
|-------------|-------------------------------------------------------|
| id          | Identificador único da pizza                          |
| name        | Nome da pizza                                         |
| description | Descrição da pizza e seus ingredientes                |
| category    | Categoria da pizza (tradicional, vegetariana ou doce) |
| price       | Preço atual da pizza                                  |
| image_name  | Nome do arquivo de imagem da pizza                    |
| available   | Indica se a pizza está disponível para venda          |
| created_at  | Data de criação do registro                           |
| updated_at  | Data da última atualização                            |

Exemplo:

```json
{
  "id": "1",
  "name": "Margherita",
  "description": "Molho de tomate, queijo e manjericão",
  "category": "tradicional",
  "price": 39.90,
  "image_name": "margherita.jpg",
  "available": true
}
```

## 4. Regras de Negócio

### RN001 - Nome da Pizza

Toda pizza deve possuir um nome obrigatório.

### RN002 - Preço da Pizza

Toda pizza deve possuir um preço maior que zero.

### RN003 - Disponibilidade

Uma pizza indisponível não deve ser apresentada como opção de compra.

### RN004 - Categoria

Toda pizza deve pertencer a uma categoria válida.

Categorias válidas:

- `tradicional`
- `vegetariana`
- `doce`

## 5. API do Serviço

O `pizza-service` disponibiliza APIs REST para consulta e gerenciamento do catálogo de pizzas.

As operações de leitura do catálogo podem ser utilizadas pelos consumidores autorizados da aplicação.

As operações de alteração do catálogo são restritas a usuários com permissão administrativa.

| Método | Endpoint       | Descrição                         | Requer Admin |
|--------|----------------|-----------------------------------|--------------|
| GET    | `/pizzas`      | Lista pizzas do catálogo          | Não          |
| GET    | `/pizzas/{id}` | Consulta detalhes de uma pizza    | Não          |
| POST   | `/pizzas`      | Cadastra uma nova pizza           | Sim          |
| PATCH  | `/pizzas/{id}` | Atualiza informações de uma pizza | Sim          |
| DELETE | `/pizzas/{id}` | Remove uma pizza do catálogo      | Sim          |

### Controle de Acesso

O controle de acesso deve ser baseado na identidade do usuário autenticado.

Usuários comuns possuem permissão somente de leitura do catálogo.

Usuários administrativos possuem permissão para alterar informações do catálogo.

O `admin-service` deve utilizar as APIs administrativas do `pizza-service`, não acessando diretamente o banco de dados do serviço.

No ambiente local, enquanto o `auth-service` não estiver implementado, as operações administrativas utilizam token Bearer configurado por `PIZZA_SERVICE_ADMIN_TOKEN`.

### Persistência NoSQL

O acesso ao Oracle NoSQL deve ser implementado exclusivamente em `app/repositories/` e a criação do client deve ficar em `app/dependencies/nosql.py`.

No ambiente `development`, o serviço utiliza `OCI_NOSQL_ENDPOINT` para conectar ao endpoint local/de desenvolvimento. Quando credenciais OCI forem necessárias, o diretório `~/.oci` do host deve ser montado no container como somente leitura em `/home/appuser/.oci`, e o serviço deve carregar as credenciais a partir de `OCI_CONFIG_FILE=/home/appuser/.oci/config` e `OCI_CONFIG_PROFILE`.

No ambiente `production`, o serviço não deve depender de arquivo de configuração OCI. A autenticação deve ocorrer por Instance Principal, usando a instância principal configurada na OCI para acessar a tabela indicada por `OCI_NOSQL_TABLE` no compartment `OCI_NOSQL_COMPARTMENT_ID`.

## 6. Critérios de Aceite

### Consulta do Catálogo

- `GET /pizzas` deve retornar HTTP 200 no padrão JSend.
- `GET /pizzas` deve retornar os dados dentro de `data.pizzas`.
- `GET /pizzas` deve retornar somente pizzas com `available=true`.
- `GET /pizzas` deve retornar uma lista vazia quando não existirem pizzas disponíveis.
- `GET /pizzas/{id}` deve retornar HTTP 200 no padrão JSend quando a pizza existir.
- `GET /pizzas/{id}` deve retornar os dados dentro de `data.pizza`.
- `GET /pizzas/{id}` deve retornar HTTP 404 no padrão JSend quando a pizza não existir.

### Gerenciamento do Catálogo

- `POST /pizzas` deve exigir usuário administrativo.
- `POST /pizzas` deve rejeitar pizza sem `name`.
- `POST /pizzas` deve rejeitar pizza com `price` menor ou igual a zero.
- `POST /pizzas` deve rejeitar pizza com `category` fora das categorias válidas.
- `PATCH /pizzas/{id}` deve exigir usuário administrativo.
- `PATCH /pizzas/{id}` deve aplicar somente os campos enviados.
- `DELETE /pizzas/{id}` deve exigir usuário administrativo.
- `DELETE /pizzas/{id}` deve retornar HTTP 404 quando a pizza não existir.

### Persistência e Contratos

- O acesso ao Oracle NoSQL deve ficar encapsulado em `app/repositories/`.
- Rotas não devem acessar diretamente o Oracle NoSQL.
- Regras de negócio e validações devem ficar em `app/services/` e `app/schemas/`.
- Todas as respostas HTTP devem seguir o padrão JSend definido em `services/AGENTS.md`.
- O contrato em `docs/api/openapi.yaml` deve ser atualizado sempre que endpoints, payloads ou respostas mudarem.
