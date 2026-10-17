# OCI Pizza - Instruções do user-service

Estas instruções complementam `services/AGENTS.md` e se aplicam somente ao
`user-service`. Em caso de conflito, estas regras específicas têm prioridade.

## Responsabilidade

O `user-service` é responsável pelo ciclo de vida dos usuários, credenciais,
confirmação de e-mail, redefinição de senha, sessões e endereços de entrega.
Também emite os access tokens JWT utilizados pelos demais serviços.

O serviço é o proprietário dos dados de usuários. Nenhum outro serviço deve
acessar suas tabelas ou coleções diretamente.

## Organização do código

- `routes/`: recebe requisições, valida schemas, chama serviços e monta
  respostas JSend.
- `services/`: concentra regras de usuários, autenticação, senhas, sessões,
  confirmação de e-mail e endereços.
- `repositories/`: encapsula a persistência de usuários, tokens, histórico de
  senhas e endereços.
- `messaging/`: abstração e implementações dos publicadores RabbitMQ e OCI
  Queue.
- `schemas/`: contratos de entrada e saída da API.
- `models/`: modelos internos e entidades persistidas.
- `dependencies/`: autenticação, persistência, mensageria e serviços
  compartilhados.

As rotas não devem conter regras de negócio, acessar repositórios diretamente
ou publicar mensagens sem passar pelo serviço responsável.

## Persistência

- SQLAlchemy/MySQL é o provider padrão do ambiente local.
- Oracle NoSQL também é suportado pela configuração existente.
- A seleção ocorre por `PERSISTENCE_PROVIDER`; não misture providers na mesma
  execução.
- O acesso deve ocorrer pelos repositórios e pela unidade de trabalho fornecida
  por injeção de dependências.
- Tokens originais, senhas e outros segredos nunca devem ser persistidos em
  texto puro.
- O `bootstrap.sh` prepara migrations, chaves locais e usuários de demonstração.
  Utilize-o somente no desenvolvimento e não sobrescreva dados reais.

## Autenticação e tokens JWT

- O login exige e-mail, senha e e-mail confirmado.
- Access tokens devem ser assinados com RS256 e conter, no mínimo, `sub`,
  `iss`, `aud`, `exp`, `is_admin` e `is_kitchen`.
- A audiência correta da aplicação é `ocipizza`.
- `is_admin=true` concede acesso às operações administrativas.
- `is_kitchen=true` identifica usuários da cozinha; essa claim não deve ser
  confundida com administrador.
- As chaves privadas devem permanecer protegidas por secrets ou pela
  configuração segura do provider OCI.
- O endpoint `/.well-known/jwks.json` deve publicar somente chaves públicas.
- Access tokens e refresh tokens não devem ser registrados em logs ou incluídos
  em mensagens de erro.

## Confirmação de e-mail e senhas

- Usuários criados pela rota pública começam com `confirmed=false`.
- Tokens de confirmação e redefinição devem ser gerados para uso único, ter
  validade limitada e ser armazenados somente como hash.
- A confirmação de e-mail deve alterar o estado do usuário de forma atômica.
- A troca de senha exige autenticação, senha atual e e-mail confirmado.
- A redefinição de senha não exige a senha atual, mas exige token válido,
  senha nova e confirmação idêntica.
- Senhas devem ser armazenadas somente como hash bcrypt e nunca retornadas em
  respostas ou mensagens.
- O fluxo de redefinição deve evitar revelar se um e-mail está cadastrado.

## Perfis administrativos

- Rotas `/admin/users` exigem `is_admin=true`.
- O contrato administrativo pode criar ou atualizar `confirmed`, `is_admin` e
  `is_kitchen` conforme os schemas administrativos existentes.
- Alterar permissões ou confirmação deve preservar as regras de autenticação e
  considerar a revogação de sessões quando aplicável.
- Usuários da cozinha não recebem acesso automático às operações
  administrativas do `user-service`.

## Endereços

- Endereços pertencem ao usuário identificado pelo token ou pelo `user_id` em
  rotas administrativas.
- Cada usuário pode possuir no máximo três endereços.
- O primeiro endereço deve ser tratado como padrão conforme a regra existente;
  somente um endereço pode ser padrão por usuário.
- CEP, estado e demais campos devem ser normalizados e validados pelos schemas
  antes da persistência.
- Não permita que um usuário consulte ou altere endereços de outro usuário.

## Mensageria

- O provider é selecionado por `MESSAGING_PROVIDER`.
- RabbitMQ utiliza `QUEUE_NAME`, `RABBITMQ_HOST`, `RABBITMQ_PORT`,
  `RABBITMQ_USERNAME` e `RABBITMQ_PASSWORD`.
- OCI Queue utiliza `OCI_QUEUE_ID`, `OCI_QUEUE_MESSAGES_ENDPOINT` e
  `OCI_REGION`, autenticando por Instance Principal.
- `OCI_QUEUE_MESSAGES_ENDPOINT` deve ser o `messagesEndpoint` específico da
  fila, não o endpoint administrativo.
- O `UserEmailService` publica solicitações; o `user-service` não envia e-mails
  diretamente.
- Os tipos atualmente publicados são `USER_CONFIRMATION` e
  `USER_PASSWORD_RESET`, contendo destinatário, nome e token quando aplicável.
- Não altere o contrato das mensagens sem atualizar o `notification-service` e
  o `README.md`.

## Contratos e qualidade

- Preserve o padrão JSend e os códigos HTTP definidos nas rotas.
- Não exponha detalhes internos de autenticação, persistência ou mensageria.
- Atualize `README.md` quando forem alterados endpoints, schemas, claims,
  providers, mensagens ou regras de segurança.
- Não crie diretórios ou arquivos de testes sem solicitação explícita.
- Preserve alterações existentes e execute apenas as validações pertinentes à
  alteração realizada.
