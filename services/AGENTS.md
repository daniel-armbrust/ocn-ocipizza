# OCI Pizza - Serviços da Aplicação - Instruções para Agentes de IA

## 1. Objetivo

Este arquivo define as regras gerais para desenvolvimento dos serviços localizados no diretório: `services/`

Estas instruções complementam o arquivo `AGENTS.md` localizado na raiz do repositório.

Antes de alterar qualquer serviço:

- Leia este arquivo

- Procure o arquivo específico de instruções para agentes do serviço: `services/<service-name>/AGENTS.md`

- Consulte a especificação do serviço para realizar o seu desenvolvimento: `services/<service-name>/docs/specs/<service-name>-spec.md`

- Consulte `services/<service-name>/docs/api/openapi.yaml` quando houver alteração em endpoints, payloads ou respostas

Quando existir um conflito, as instruções mais específicas do serviço possuem prioridade.

## 2. Descrição dos Serviços da Aplicação

A aplicação OCI Pizza é composta pelos seguintes serviços:

- Serviço responsável pelo domínio do catálogo de pizzas: `services/pizza-service/`

- Serviço responsável pelo domínio de autenticação e gerenciamento de identidade: `services/auth-service/`

- Serviço responsável pelo domínio de gerenciamento de usuários e dados de perfil: `services/user-service/`

- Serviço responsável pelo domínio de criação e gerenciamento de pedidos: `services/order-service/`

- Serviço responsável pelo domínio de processamento de pagamentos: `services/payment-service/`

- Serviço responsável pelo domínio de envio de notificações aos usuários: `services/notification-service/`

- Serviço responsável pelo domínio de interação conversacional e recursos de IA: `services/chatbot-service/`

- Serviço responsável pela interface web da aplicação: `services/frontend-service/`

- Serviço responsável pelas operações administrativas da aplicação: `services/admin-service/`

## 3. APIs REST e Interfaces Web

Serviços que expõem APIs REST devem seguir boas práticas que são:

- Utilizar nomes de recursos no plural
- Utilizar métodos HTTP corretamente
- Utilizar códigos HTTP apropriados
- Manter contratos estáveis

O contrato técnico das APIs deve ser mantido atualizado através da especificação OpenAPI do serviço em: `services/<service-name>/docs/api/openapi.yaml`

Serviços que não expõem API própria, como `frontend-service`, não devem possuir OpenAPI por padrão. Nesses casos, o serviço deve documentar na SPEC quais APIs consome e como renderiza ou utiliza os dados obtidos.

### Padrão de Resposta

Todas as APIs REST dos serviços devem utilizar o padrão JSend (https://github.com/omniti-labs/jsend).

O objetivo é manter consistência entre os microsserviços e facilitar o consumo das APIs.

Resposta de sucesso:

```json
{
  "status": "success",
  "data": {
    "id": "123",
    "name": "Margherita"
  }
}
```

```json
{
  "status": "success",
  "data": {
    "pizzas": [
      {
        "id": "pizza-001",
        "name": "Margherita",
        "description": "Molho de tomate, queijo e manjericão",
        "category": "Tradicional",
        "price": 39.90,
        "available": true
      },
      {
        "id": "pizza-002",
        "name": "Calabresa",
        "description": "Molho de tomate, queijo e calabresa",
        "category": "Tradicional",
        "price": 42.90,
        "available": true
      }
    ]
  }
}
```

Resposta de falha de validação:

```json
{
  "status": "fail",
  "data": {
    "field": "name",
    "code": "VALIDATION_REQUIRED",
    "message": "Field is required"
  }
}
```

Resposta de erro inesperado:

```json
{
  "status": "error",
  "message": "Internal server error"
}
```

## 4. Comunicação entre Serviços

Serviços não devem acessar diretamente o banco de dados de outro serviço. Ou seja, cada serviço deve ser proprietário dos seus dados.

- Exemplo proibido: `order-service` -> `user-service database`

A comunicação deve ocorrer através de:

- APIs
- Eventos
- Mecanismos definidos pela arquitetura

Cada serviço deve expor contratos claros de comunicação.

Alterações em contratos existentes devem avaliar impacto nos consumidores.

## 5. Desenvolvimento Local

Cada serviço deve ser executável no ambiente local utilizando os mecanismos definidos pelo projeto.

Antes de alterar qualquer um dos arquivos `Dockerfile`, `requirements.txt` e `docker-compose.yaml`, avalie o impacto no ambiente local e nos demais serviços dependentes.

Alterações que adicionem dependências devem atualizar o arquivo `requirements.txt` e validar a construção da imagem Docker.

## 6. Containers

Cada serviço deve possuir os arquivos `Dockerfile` e `.dockerignore`.

O arquivo `Dockerfile` deve:

- Possuir apenas dependências necessárias
- Utilizar imagens base apropriadas
- Evitar inclusão de arquivos desnecessários

O arquivo `.dockerignore` de cada serviço deve evitar copiar:

- Arquivos temporários
- Caches
- Arquivos de desenvolvimento local
- Documentação desnecessária para execução da aplicação
- Informações sensíveis

## 7. Estrutura Interna do Serviço

Os serviços devem seguir separação de responsabilidades conforme sua natureza:

- `routes/` não devem conter regras de negócio.
  - Responsabilidade: receber requisições HTTP, validar entrada, chamar serviços e retornar respostas.

- `services/` devem concentrar regras de negócio da aplicação.
  - Responsabilidade: implementar lógica de domínio, validações e orquestração de operações.

- `repositories/` devem encapsular o acesso aos dados.
  - Responsabilidade: realizar operações de persistência e abstrair detalhes do banco de dados ou mecanismos de armazenamento.

- `schemas/` devem definir os contratos de entrada e saída da aplicação.
  - Responsabilidade: validar dados recebidos, estruturar respostas da API e representar modelos de comunicação entre camadas.

- `models/` devem representar os modelos internos da aplicação.
  - Responsabilidade: representar entidades persistidas ou objetos de domínio utilizados internamente.

- `dependencies/` devem concentrar componentes reutilizáveis utilizados pela aplicação.
  - Responsabilidade: disponibilizar recursos compartilhados como autenticação, conexões, configurações e injeção de dependências.

Serviços de interface web, como `frontend-service`, podem possuir estruturas específicas de apresentação:

- `templates/`
  - Responsabilidade: concentrar templates HTML renderizados pelo serviço.

- `static/`
  - Responsabilidade: concentrar arquivos estáticos, como CSS, JavaScript e imagens.

- `clients/`
  - Responsabilidade: concentrar clientes HTTP para consumo das APIs dos demais serviços.
  - Deve ser organizado em um módulo por serviço consumido.

Serviços de interface web não devem implementar regras de negócio dos domínios consumidos nem acessar diretamente bancos de dados de outros serviços.

## 8. Código

Os serviços devem ser desenvolvidos utilizando a linguagem de programação Python e seguir padrões consistentes de qualidade, organização e manutenção de código.

Todo código Python deve:

- Seguir as recomendações da `PEP 8`
- Utilizar docstrings conforme a `PEP 257` quando necessário
- Utilizar type hints
- Manter padrões consistentes de nomenclatura, organização e documentação
- Possuir código legível e de fácil manutenção
- Quebras de linha em instruções Python devem priorizar legibilidade, usando parênteses para continuidade implícita e evitando barras invertidas (`\`) sempre que possível.
- Em chamadas de função, definições com vários parâmetros, coleções e imports distribuídos em várias linhas, utilizar vírgula final quando isso melhorar a legibilidade e facilitar futuras alterações.
- Não adicionar vírgula após o nome de uma função ou método sem argumentos, nem no alvo de um `for`, pois isso pode criar uma tupla de um elemento ou alterar a semântica do desempacotamento. A vírgula nesses casos só deve ser usada quando essa semântica for intencional e estiver clara no código.

A qualidade do código deve ser verificada automaticamente utilizando ferramentas de:

- Linting
- Formatação
- Análise estática
- Testes automatizados

Tecnologias e padrões utilizados quando aplicável:

- FastAPI para desenvolvimento de APIs REST ou renderização de páginas HTML
- Pydantic para validação e modelagem de dados
- Python Type Hints para definição explícita de tipos
- Pytest para testes automatizados.

O código deve preferencialmente utilizar gerenciamento de dependências através de arquivos padronizados pelo projeto.

Não adicionar bibliotecas sem avaliar impacto e necessidade.

### Qualidade do Código

Antes de considerar uma alteração concluída, execute as ferramentas definidas pelo projeto.

- formatter
- linter
- Testes automatizados.

O agente deve consultar o `Makefile` localizado na raiz do projeto para identificar os comandos oficiais de validação.

## 8. Testes

Toda alteração de código deve considerar testes em: `services/<service-name>/tests/`

Tipos esperados:

### Testes Unitários

Para:

- Regras de negócio
- Validações
- Funções isoladas

### Testes de Integração

Para:

- Persistência
- Integrações externas
- Componentes internos

### Testes de API

Para:

- Endpoints REST
- Contratos HTTP

### Testes de Interface Web

Para:

- Rotas de páginas HTML
- Renderização de templates
- Tratamento de indisponibilidade de serviços consumidos

Novas funcionalidades devem incluir testes quando aplicável.

## 9. Especificação e Contrato de API

Antes de implementar alterações em um serviço, o agente deve consultar:

- `docs/specs/`
    - Para entender requisitos funcionais, regras do domínio, decisões relevantes e limites arquiteturais do serviço.

- `docs/api/openapi.yaml`
    - Para alterações relacionadas aos contratos da API, quando o serviço expuser API própria.

Quando uma alteração envolver:

- Nova funcionalidade
- Mudança de arquitetura
- Nova integração
- Alteração de contrato

O agente deve atualizar a SPEC do serviço e, quando aplicável, o OpenAPI.

O `README.md` do serviço deve ser revisado em toda alteração relevante no serviço e atualizado quando houver mudança em responsabilidades, estrutura interna, comandos de execução, variáveis de ambiente, endpoints ou comportamento documentado.

Para evitar excesso de documentação, novos documentos em `docs/plans/`, `docs/decisions/` ou diretórios equivalentes não devem ser criados por padrão. Use esses formatos somente se houver solicitação explícita ou necessidade excepcional justificada.

## 10. Definition of Done do Serviço

Uma alteração em um serviço está concluída quando:

### Código

- Implementação concluída
- Arquitetura respeitada
- Padrões existentes mantidos

### Testes

- Testes adicionados quando necessário
- Testes existentes continuam funcionando

### Documentação

Quando aplicável:

- Especificação atualizada
- OpenAPI atualizado
- `README.md` do serviço revisado e atualizado quando a alteração impactar responsabilidades, estrutura, execução, configuração, endpoints ou comportamento documentado

### Container

Quando aplicável:

- `Dockerfile` atualizado
- `requirements.txt` atualizado
- Imagem validada

### Integração

Quando aplicável:

- Contratos de API revisados
- Impacto em outros serviços avaliado

### Segurança

- Nenhuma informação sensível adicionada.
- Dependências avaliadas quando adicionadas.
- Validações de entrada mantidas.
