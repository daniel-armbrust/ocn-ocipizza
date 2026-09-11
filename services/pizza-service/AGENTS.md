# OCI Pizza - Pizza Service - Instruções para Agentes de IA

## 1. Objetivo

Este arquivo contém instruções específicas para o serviço `services/pizza-service/` que é responsável pelo domínio do catálogo de pizzas da aplicação OCI Pizza. 

## 2. Documentação do Serviço

A documentação do `pizza-service` está localizada em:

- `docs/specs/`
- `docs/api/`

## 3. Ordem Obrigatória de Consulta

Antes de implementar qualquer alteração no `pizza-service`, leia nesta ordem:

1. `../../AGENTS.md`
2. `../AGENTS.md`
3. `AGENTS.md`
4. `docs/specs/pizza-service-spec.md`
5. `docs/api/openapi.yaml`, quando a alteração envolver endpoints, payloads ou respostas

Se a alteração envolver persistência, padrão de resposta HTTP, autenticação ou autorização, registre o contexto necessário diretamente em:

- `docs/specs/pizza-service-spec.md`, para decisões funcionais, regras de domínio e limites arquiteturais
- `docs/api/openapi.yaml`, para contratos de API

Quando existir conflito entre documentos, a instrução mais específica deve prevalecer, desde que não viole regras de segurança ou contratos já documentados.

### Documentação Enxuta

O `pizza-service` deve manter apenas dois artefatos documentais obrigatórios:

- SPEC: `docs/specs/pizza-service-spec.md`
- API: `docs/api/openapi.yaml`

Planos de implementação, ADRs e documentos auxiliares não devem ser criados por padrão. Use esses formatos somente se houver solicitação explícita ou necessidade excepcional justificada.

Outros serviços devem consumir este domínio através das APIs disponibilizadas.
