# OCI Pizza - Instruções para Agentes de IA

## 1. Objetivo

Este arquivo define as regras gerais para agentes de IA que trabalham neste repositório que deve ser considerado a fonte de verdade para contexto, decisões e padrões.

O agente deve atuar como um membro de uma equipe de engenharia de software, seguindo processos definidos, respeitando arquitetura, documentação, segurança e qualidade.

Antes de iniciar qualquer tarefa o agente DEVE:

- Entender o contexto antes de modificar arquivos
- Consultar documentação existente
- Realizar alterações pequenas e verificáveis
- Preservar padrões existentes
- Evitar complexidade desnecessária
- Manter código e documentação consistentes

O objetivo não é apenas gerar código e sim manter um sistema:

- Compreensível
- Seguro
- Testável
- Documentado
- Evolutivo

## 2. Contexto da Aplicação

OCI Pizza é uma aplicação cloud-native de referência utilizada para demonstrar:

- Desenvolvimento de Aplicações Modernas em OCI
- Arquitetura de Microsserviços
- Deployment multi-region
- APIs REST
- Containers
- Kubernetes
- Infrastructure as Code (IaC)
- CI/CD
- Desenvolvimento Assistido por Agentes de IA

## 3. Estrutura do Monorepo

Este repositório utiliza uma estrutura monorepo onde os seus diretórios estão descritos a seguir:

### services/

Diretório que contém o código dos serviços da aplicação.

As regras gerais e boas práticas para o desenvolvimento dos serviços ficam em: `services/AGENTS.md`

Cada serviço possui seu próprio contexto e pode possuir seu arquivo `AGENTS.md` específico, que complementa as regras gerais.

Por exemplo, para o serviço `pizza-service`, consulte o arquivo
`services/pizza-service/AGENTS.md` e o `README.md` do serviço.

Antes de alterar um serviço, procure instruções específicas em seu diretório e
consulte a documentação que realmente existir.

### terraform/

Diretório que contém o código e documentação relacionada à infraestrutura como código.

Alterações neste diretório devem considerar as instruções em
`terraform/AGENTS.md` e os arquivos de configuração existentes.

### kubernetes/

Diretório que contém manifestos, configurações e documentação relacionada ao Kubernetes.

Alterações neste diretório devem considerar as instruções em
`kubernetes/AGENTS.md` e os manifestos existentes.

### cicd/

Diretório que contém automações de integração contínua e entrega contínua.

Responsabilidades:

- Execução de Pipelines
- Validações Automáticas
- Construção de Artefatos
- Automações de Entrega

## 4. Desenvolvimento Local

O ambiente local deve utilizar as ferramentas e comandos definidos pelo projeto.

O ambiente local deve ser executado preferencialmente utilizando: `docker compose up`

Consulte: `docker-compose.yaml` e `Makefile`.

Evite criar comandos paralelos quando já existir uma automação definida.

Quando uma decisão arquitetural relevante for tomada, registre-a de forma
objetiva no `README.md` do componente afetado, salvo solicitação explícita de
outro formato.

## 5. Controle Git

O agente deve preservar alterações existentes no repositório e evitar operações destrutivas.

Alterações já existentes, alterações feitas manualmente pelo usuário ou alterações realizadas por outros agentes/processos devem ser consideradas intencionais e NÃO devem ser desfeitas, sobrescritas ou revertidas sem solicitação explícita do usuário.

O agente NÃO deve executar automaticamente:

- `git commit`
- `git push`
- `git merge`
- `git rebase`
- Alterações de Histórico Git

O agente pode:

- Criar e modificar arquivos dentro do diretório raiz e seus subdiretórios
- Executar testes
- Analisar alterações
- Sugerir boas práticas 
- Sugerir comandos Git

## 6. Idioma

- Toda documentação e mensagens de commit devem ser escritas em português do Brasil.

- Nomes de classes, funções, variáveis e arquivos de código devem permanecer em inglês.

- Comentários no código devem ser escritos em português do Brasil somente quando agregarem contexto relevante.

- Termos técnicos consolidados, como FastAPI, Repository Pattern, Dependency Injection e NetworkPolicy, não precisam ser traduzidos.

## 7. Pull Requests (PR)

O agente pode auxiliar preparando:

- Descrição do Pull Request (PR)
- Resumo das Alterações
- Checklist de Revisão
- Análise de Impacto.

O agente NÃO deve:

- Criar merge automaticamente
- Aprovar alterações automaticamente
- Publicar código sem autorização

## 8. Regras de Segurança

Nunca:

- Armazenar senhas no código
- Adicionar tokens ou chaves privadas ao repositório
- Versionar arquivos contendo segredos
- Expor informações sensíveis
- Remover controles de segurança sem justificativa
- Criar, excluir, mover ou editar arquivos fora da raiz deste repositório
- Gerar artefatos, scripts, arquivos temporários ou documentação fora deste repositório
- Realizar alterações externas ao repositório sem instrução explícita

Sempre:

- Utilizar mecanismos apropriados para configuração sensível
- Validar entradas externas
- Aplicar princípio do menor privilégio
- Considerar impacto de segurança antes e depois das alterações

## 9. Documentação e fluxo de trabalho

Para funcionalidades relevantes, o fluxo esperado é:

1. Entendimento do contexto e dos contratos existentes
2. Implementação pequena e verificável
3. Validação pertinente
4. Revisão

Antes de implementar uma funcionalidade nova, consulte o `README.md`, os
`AGENTS.md` aplicáveis e os arquivos de código relacionados. Atualize o
`README.md` quando houver mudança em responsabilidades, configuração,
integrações, endpoints ou comportamento.

Não crie planos, ADRs, SPECs, contratos OpenAPI ou outros documentos auxiliares
sem solicitação explícita.

## 10. Definition of Done

Uma tarefa somente está concluída quando:

### Implementação

- Alteração implementada
- Solução segue os padrões existentes
- Impacto em outros componentes foi avaliado

### Validação

- Validações pertinentes executadas quando aplicável
- Testes existentes preservados e executados quando aplicável
- Nenhum arquivo ou diretório de testes criado sem solicitação explícita
- Problemas encontrados foram corrigidos

### Revisão

- Alterações revisadas antes de serem consideradas concluídas.
- Código preparado para revisão via Pull Request quando aplicável.

### Documentação

Quando aplicável:

- `README.md` atualizado quando aplicável
