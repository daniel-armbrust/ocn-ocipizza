# OCI Pizza

![Logo OCI Pizza](docs/img/ocipizza-logo.png)

O OCI Pizza é uma aplicação cloud native de referência criada para estudar, na
prática, conceitos de arquitetura de microsserviços e desenvolvimento de
aplicações modernas na Oracle Cloud Infrastructure (OCI).

O projeto demonstra separação de domínios, APIs REST, autenticação,
mensageria, persistência, armazenamento de objetos, containers, observabilidade,
infraestrutura como código e execução local e no OCI.

Toda a aplicação é desenvolvida em Python 3.11, utilizando FastAPI como
principal framework para as APIs REST, serviços web e integração com os
componentes da arquitetura.

A aplicação foi projetada para executar localmente com Docker Compose e para
ser implantada na OCI utilizando os mesmos serviços e contratos. O ambiente
local substitui serviços gerenciados por componentes compatíveis, permitindo
desenvolvimento sem dependência de uma conta OCI. Na OCI, endpoints,
credenciais e autenticação são trocados pelas configurações dos serviços
gerenciados, mantendo a mesma aplicação e o mesmo comportamento esperado.

## Disclaimer

Este repositório é um projeto de estudos **NÃO OFICIAL**, criado para
demonstrar conceitos de desenvolvimento de aplicações cloud-native,
microsserviços, containers, Kubernetes, Infrastructure as Code e serviços da
Oracle Cloud Infrastructure (OCI).

O conteúdo reflete exclusivamente o entendimento e as experiências do autor.
Ele **NÃO SUBSTITUI** a documentação oficial da Oracle e é disponibilizado
**SEM GARANTIAS** de funcionamento, precisão, segurança, compatibilidade ou
adequação para ambientes de produção.

A OCI evolui continuamente, com novos serviços, funcionalidades, versões e
mudanças em limites, preços e comportamentos. Por isso, exemplos,
configurações e procedimentos deste repositório podem ficar desatualizados.

O autor não se responsabiliza por perdas, danos, indisponibilidade, custos,
incidentes de segurança ou quaisquer outras consequências, diretas ou
indiretas, decorrentes do uso total ou parcial deste conteúdo. A utilização
dos exemplos, códigos e configurações deste repositório é de inteira
responsabilidade do usuário.

Antes de utilizar qualquer conteúdo, especialmente em ambientes reais,
consulte a [documentação oficial da Oracle Cloud Infrastructure](https://docs.oracle.com/en-us/iaas/Content/home.htm),
revise os impactos de segurança e custos e adapte as configurações às
necessidades do seu ambiente.

## Instruções para agentes (`AGENTS.md`)

O repositório possui arquivos `AGENTS.md` distribuídos pelos diretórios para
registrar contexto, padrões e regras de trabalho para agentes de IA e demais
colaboradores. Esses arquivos existem para preservar decisões do projeto,
evitar alterações incompatíveis e manter a implementação consistente.

- O `AGENTS.md` da raiz define as regras gerais do monorepo, segurança,
  documentação, controle Git e fluxo de trabalho.
- O `services/AGENTS.md` define os padrões compartilhados pelos microsserviços,
  como organização interna, comunicação entre serviços, respostas HTTP e
  validação.
- Cada diretório de serviço pode possuir seu próprio `AGENTS.md`, com regras
  específicas da responsabilidade e da arquitetura daquele serviço. Essas
  instruções complementam as regras gerais e têm prioridade quando houver uma
  particularidade do serviço.
- Os diretórios de infraestrutura e automação podem possuir instruções próprias
  para orientar alterações em Kubernetes, Terraform ou CI/CD.

Antes de alterar qualquer componente, consulte o `AGENTS.md` da raiz, os
arquivos aplicáveis aos diretórios envolvidos e o `README.md` do serviço. As
instruções mais específicas devem ser consideradas em conjunto com as regras
gerais do repositório.

## Microsserviços

Cada microsserviço possui um `README.md` próprio. Consulte esse arquivo antes
de alterar ou integrar um serviço, pois ele contém responsabilidades,
configurações, endpoints, dependências e instruções específicas.

| Serviço | Responsabilidade |
| --- | --- |
| `user-service` | Usuários, autenticação, tokens JWT, confirmação de e-mail, senhas, sessões e endereços. |
| `pizza-service` | Catálogo de pizzas, categorias, preços, disponibilidade e imagens. |
| `delivery-service` | Áreas de entrega, faixas de CEP, taxa e prazo estimado. |
| `order-service` | Criação, consulta, atualização e administração de pedidos, preservando snapshots da compra. |
| `notification-service` | Consumo de mensagens e envio de e-mails transacionais. |
| `frontend-service` | Interface web pública e BFF para sessões, formulários e chamadas aos microsserviços. |
| `admin-service` | Painel administrativo para usuários, pizzas, entregas, pedidos e operações da cozinha. |
| `chatbot-service` | |

<!-- TODO: Documentar a responsabilidade do chatbot-service quando a implementação estiver disponível. -->

Os serviços são proprietários dos seus próprios dados. A comunicação entre
domínios ocorre por APIs ou mensagens, nunca por acesso direto ao banco de
dados de outro microsserviço.

## Serviços utilizados na OCI

| Capacidade | Serviço OCI | Uso no OCI Pizza |
| --- | --- | --- |
| Persistência NoSQL | OCI NoSQL | Catálogo, pedidos e áreas de entrega, conforme o provider configurado. |
| Persistência relacional | MySQL Database Service | Dados relacionais do `user-service` e providers alternativos. |
| Cache e sessões | OCI Cache | Sessões e dados temporários quando o Redis local for substituído na OCI. |
| Observabilidade | OCI Logging | Centralização dos logs fora do ambiente local. |
| Execução de containers | Container Instances | Execução de containers sem gerenciamento direto de nós. |
| Orquestração | OKE | Execução orquestrada dos microsserviços em Kubernetes. |
| Imagens | Container Registry | Armazenamento e distribuição das imagens dos serviços. |
| Arquivos e imagens | Object Storage | Imagens das pizzas e outros objetos. |
| E-mails | Email Delivery | Envio de e-mails transacionais. |
| Mensageria | OCI Queue | Publicação e consumo de notificações assíncronas. |

Os serviços locais equivalentes imitam as funcionalidades necessárias da OCI:

| Serviço OCI | Componente local equivalente |
| --- | --- |
| OCI NoSQL | Container `nosql` |
| MySQL Database Service | Container `mysql` |
| OCI Cache | Container `redis` |
| OCI Logging | Logs enviados para `stdout` |
| Container Instances/OKE | Docker Compose local e manifestos Kubernetes |
| Container Registry | Imagens construídas localmente pelo Docker |
| Object Storage | Container `object-storage`, baseado em MinIO |
| Email Delivery | Container `mailpit`, acessado por SMTP |
| OCI Queue | Container `rabbitmq` |

Essa infraestrutura local existe justamente para imitar os fluxos essenciais
da OCI e permitir que a aplicação seja executada localmente com o mesmo modelo
de integração utilizado no ambiente OCI.

## Execução local

O ambiente local deve ser executado a partir da raiz do repositório usando o
`docker-compose.yaml` e os alvos do `Makefile`. Essa é a forma recomendada,
pois garante a ordem de inicialização, a rede e as configurações esperadas.

Para consultar os comandos disponíveis:

```bash
make help
```

Para iniciar a infraestrutura, aguardar sua disponibilidade e iniciar todos os
microsserviços:

```bash
make development
```

Para iniciar somente a infraestrutura:

```bash
make development-infra
```

Para iniciar somente os microsserviços quando a infraestrutura já estiver
disponível:

```bash
make development-services
```

### Homologação local utilizando recursos reais do OCI

O projeto também permite executar os containers localmente utilizando os
providers reais do OCI. Esse fluxo não faz deployment na OCI: os processos
continuam sendo executados pelo Docker Compose na máquina local, mas podem
acessar OCI NoSQL, OCI Object Storage, OCI Queue e OCI Email Delivery.

Crie o arquivo local `.env.oci` (ele é ignorado pelo Git) e informe os
identificadores da tenancy e os parâmetros de autenticação. No mínimo, o
ambiente precisa definir:

- `NOSQL_COMPARTMENT_ID`;
- `OCI_QUEUE_ID` da fila `notifications-queue`;
- `OCI_EMAIL_DELIVERY_COMPARTMENT_ID`;
- `OCI_AUTH_MODE=config_file` e `OCI_HOST_CONFIG_FILE`, quando for utilizada
  autenticação por arquivo; ou `OCI_AUTH_MODE=instance_principal` quando a
  identidade OCI estiver disponível no ambiente de execução.

Depois, carregue as variáveis no shell e inicie o ambiente:

```bash
${EDITOR:-vi} .env.oci
source ./scripts/use-oci-env.sh
make development-oci
```

O script `scripts/use-oci-env.sh` valida a configuração e exporta os
providers `oci`, `oci_queue` e `oci` para NoSQL, Object Storage, mensageria e
e-mail, respectivamente. O alvo `development-oci` usa essas variáveis ao
iniciar os microsserviços. As dependências locais ainda declaradas no
`docker-compose.yaml`, como Redis ou MySQL quando necessárias por um serviço,
continuam sendo iniciadas localmente.

Esse fluxo é uma homologação local da integração com OCI. Ele não substitui o
bootstrap dos recursos, a configuração de IAM, a montagem do arquivo OCI nos
containers ou um deployment em Container Instances/OKE.

Para executar os `bootstrap.sh` dos serviços que possuem esse script:

```bash
make development-bootstrap
```

Os bootstraps podem recriar tabelas e dados de demonstração. Execute esse alvo
somente quando a reinicialização do ambiente local for desejada.

### Build e rebuild

Os comandos de construção atuam somente nos microsserviços da aplicação; não
reconstroem MySQL, NoSQL, RabbitMQ, Redis, Object Storage ou Mailpit:

```bash
make build
make rebuild
make development-rebuild
```

`build` utiliza o cache disponível. `rebuild` reconstrói as imagens sem cache.
`development-rebuild` reconstrói os microsserviços e inicia o ambiente de
desenvolvimento novamente.

### Logs e encerramento

```bash
make development-logs
make development-down
```

Também é possível utilizar diretamente o Compose:

```bash
docker compose up -d
docker compose ps
docker compose logs -f
docker compose down
```

## Portas locais

| Componente | Porta no host |
| --- | ---: |
| `pizza-service` | `8001` |
| `user-service` | `8002` |
| `delivery-service` | `8003` |
| `order-service` | `8004` |
| `notification-service` | `8005` |
| `admin-service` | `8006` |
| `frontend-service` | `8010` |
| MySQL | `13306` |
| Oracle NoSQL | `18080` |
| RabbitMQ | `5672` |
| Redis | `16379` |
| Object Storage/MinIO | `9000` |
| Mailpit SMTP | `1025` |
| Mailpit Web UI | `8025` |

## Configuração e segurança

Os arquivos `.env.example` de cada serviço documentam as configurações locais.
Não versione arquivos `.env`, senhas, tokens, chaves privadas ou outros
segredos. Em ambientes OCI, prefira Instance Principal, Dynamic Groups, IAM
Policies e serviços de secrets em vez de credenciais estáticas.

## Qualidade e CI/CD

<!-- TODO: Implementar e documentar os comandos compartilhados de lint. -->
<!-- TODO: Implementar e documentar os testes automatizados. -->
<!-- TODO: Documentar os fluxos de CI/CD. -->

Consulte o `README.md` de cada microsserviço para obter instruções específicas
de execução, configuração e operação.
