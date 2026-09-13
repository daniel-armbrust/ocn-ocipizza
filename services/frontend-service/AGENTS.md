# OCI Pizza - Frontend Service - Instruções para Agentes de IA

## 1. Objetivo

Este arquivo contém instruções específicas para o serviço `services/frontend-service/`, responsável pela interface web da aplicação OCI Pizza.

## 2. Documentação do Serviço

A documentação do `frontend-service` está localizada em:

- SPEC: `docs/specs/frontend-service-spec.md`
- README: `README.md`

O `frontend-service` não expõe API própria.

## 3. Ordem Obrigatória de Consulta

Antes de implementar ou modificar o serviço `frontend-service`, consultar obrigatoriamente, nesta ordem:

1. `../../AGENTS.md`
2. `../AGENTS.md`
3. `AGENTS.md`
4. `docs/specs/frontend-service-spec.md`
5. `README.md`

## 4. Regras Específicas

- O `frontend-service` deve concentrar apenas responsabilidades de apresentação e integração com APIs dos demais serviços.

- Clients HTTP devem ficar em `app/clients/`, organizados em um módulo por serviço consumido.

- Regras de negócio pertencentes aos domínios da aplicação devem permanecer nos serviços responsáveis.

- Alterações em telas, rotas, configuração, variáveis de ambiente ou integrações devem manter o `README.md` atualizado.

- Alterações que afetem contratos de API devem ser alinhadas com o serviço proprietário do contrato.

Quando existir conflito entre documentos, a instrução mais específica deve prevalecer, desde que não viole regras de segurança ou contratos já documentados.
