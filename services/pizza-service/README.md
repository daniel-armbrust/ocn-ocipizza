# OCI Pizza - Pizza Service

## 1. Visão Geral

O `pizza-service` é um microsserviço responsável pelo domínio de catálogo de pizzas da aplicação OCI Pizza.

Este serviço disponibiliza APIs REST para consulta e gerenciamento das informações relacionadas ao catálogo de pizzas.

O `pizza-service` é o proprietário dos dados relacionados ao catálogo.

## 2. Responsabilidades

O `pizza-service` permite:

- Consultar pizzas do catálogo
- Consultar detalhes de uma pizza
- Cadastrar novas pizzas
- Atualizar informações de pizzas
- Controlar disponibilidade dos produtos

O serviço NÃO é responsável por:

- Autenticação de usuários
- Gerenciamento de identidade
- Gerenciamento de usuários
- Criação de pedidos
- Processamento de pagamentos
- Envio de notificações
- Interface gráfica da aplicação

## 3. Tecnologias

O serviço utiliza:

- Python
- FastAPI
- Pydantic
- pytest

## 4. Estrutura e Descrição dos Arquivos e Diretórios

```text
pizza-service/
├── app/
│   │
│   ├── main.py
│   │
│   ├── routes/
│   │   └── pizza_routes.py
│   │
│   ├── services/
│   │   └── pizza_service.py
│   │
│   ├── repositories/
│   │   └── pizza_repository.py
│   │
│   ├── schemas/
│   │   └── pizza_schema.py
│   │
│   ├── models/
│   │   └── pizza_model.py
│   │
│   └── dependencies/
│       ├── auth.py
│       └── nosql.py
│
├── tests/
│   │
│   ├── unit/
│   │   └── test_pizza_service.py
│   │
│   ├── integration/
│   │   └── test_pizza_repository.py
│   │
│   └── api/
│       └── test_pizza_api.py
│
├── docs/
│   │
│   ├── specs/
│   │   └── pizza-service-spec.md
│   │
│   └── api/
│       └── openapi.yaml
│
├── Dockerfile
├── requirements.txt
├── .dockerignore
├── .env.example
├── AGENTS.md
└── README.md
```

- `app/`
    - Contém o código principal da aplicação.

- `app/main.py`
    - Ponto de entrada da aplicação FastAPI.
    - Responsável pela inicialização da aplicação e registro dos componentes principais.

- `app/routes/pizza_routes.py`
    - Contém as rotas HTTP da API.
    - Responsável por receber requisições, validar entradas e retornar respostas HTTP.

- `app/services/pizza_service.py`
    - Contém as regras de negócio do domínio.
    - Responsável pela implementação dos casos de uso relacionados às pizzas.

- `app/repositories/pizza_repository.py`
    - Contém a camada de acesso aos dados.
    - Responsável por encapsular operações de persistência no Oracle NoSQL.

- `app/schemas/pizza_schema.py`
    - Contém os modelos de entrada e saída utilizados pela API.
    - Responsável pela validação e padronização dos contratos HTTP.

- `app/models/pizza_model.py`
    - Contém os modelos internos utilizados pela aplicação.
    - Representa entidades e estruturas utilizadas pelo serviço.

- `app/dependencies/`
    - Contém componentes compartilhados utilizados pela aplicação.

- `app/dependencies/nosql.py`
    - Responsável por disponibilizar o cliente e configurações de acesso ao Oracle NoSQL.

- `app/dependencies/auth.py`
    - Responsável por validar autenticação e autorização quando endpoints administrativos forem implementados.

- `tests/`
    - Contém os testes automatizados do serviço.

- `tests/unit/test_pizza_service.py`
    - Contém testes unitários das regras de negócio.

- `tests/api/test_pizza_api.py`
    - Contém testes dos endpoints REST da aplicação.

- `tests/integration/test_pizza_repository.py`
    - Contém testes de integração relacionados à persistência e componentes externos.

- `docs/`
    - Contém a documentação do serviço.

- `docs/specs/pizza-service-spec.md`
    - Contém a especificação funcional do serviço.

- `docs/api/openapi.yaml`
    - Contém a documentação técnica e contrato da API.

Por padrão, a documentação obrigatória do serviço deve ficar limitada à SPEC e ao contrato OpenAPI. Planos, ADRs e documentos auxiliares só devem ser adicionados quando houver solicitação explícita ou necessidade excepcional justificada.

- `Dockerfile`
    - Define como a imagem Docker do serviço será construída.

- `.dockerignore`
    - Define arquivos que não devem ser enviados durante a construção da imagem Docker.

- `requirements.txt`
    - Lista as dependências Python utilizadas pelo serviço.

- `.env.example`
    - Arquivo de referência contendo as variáveis de ambiente necessárias para execução do serviço.
    - Não deve conter informações sensíveis.

- `README.md`
    - Documentação inicial do serviço.

- `AGENTS.md`
    - Arquivo de instruções específicas para agentes de IA que trabalham neste serviço.
    - Complementa as instruções definidas nos arquivos `AGENTS.md` da raiz e do diretório `services/`.
