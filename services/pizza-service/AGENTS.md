# OCI Pizza - Pizza Service - Instruções para Agentes de IA

## 1. Objetivo

Este arquivo contém instruções específicas para o serviço `services/pizza-service/` que é responsável pelo domínio do catálogo de pizzas da aplicação OCI Pizza. 

## 2. Documentação do Serviço

A documentação do `pizza-service` está localizada em:

- SPEC: `docs/specs/pizza-service-spec.md`
- API: `docs/api/openapi.yaml`
- README: `README.md`

## 3. Ordem Obrigatória de Consulta

Antes de implementar ou modificar o serviço `pizza-service`, consultar obrigatoriamente, nesta ordem:

1. `../../AGENTS.md`
2. `../AGENTS.md`
3. `AGENTS.md`
4. `docs/specs/pizza-service-spec.md`
5. `docs/api/openapi.yaml`, quando a alteração envolver endpoints, payloads ou respostas
6. `README.md`

## 4. Regras Específicas

- O `pizza-service` deve concentrar apenas responsabilidades do domínio de catálogo de pizzas.

- O serviço é a fonte de verdade para pizzas, categorias, preços, imagens e disponibilidade dos produtos.

- Regras de negócio e validações do catálogo devem permanecer em `app/services/` e `app/schemas/`.

- Rotas HTTP não devem acessar diretamente mecanismos de persistência ou conter regras de negócio.

- O acesso ao Oracle NoSQL deve ficar encapsulado em `app/repositories/` e `app/dependencies/nosql.py`.

- Operações de alteração do catálogo devem exigir permissão administrativa.

- Alterações em endpoints, payloads ou respostas devem manter `docs/api/openapi.yaml` atualizado.

- Alterações em responsabilidades, estrutura, execução, configuração, endpoints ou comportamento documentado devem manter o `README.md` atualizado.

Se a alteração envolver persistência, padrão de resposta HTTP, autenticação ou autorização, registre o contexto necessário diretamente em:

- `docs/specs/pizza-service-spec.md`, para decisões funcionais, regras de domínio e limites arquiteturais

- `docs/api/openapi.yaml`, para contratos de API

Quando existir conflito entre documentos, a instrução mais específica deve prevalecer, desde que não viole regras de segurança ou contratos já documentados.
