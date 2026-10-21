# OCI Pizza - Instruções do pizza-service

Estas instruções complementam `services/AGENTS.md` e se aplicam somente ao
`pizza-service`. Em caso de conflito, estas regras específicas têm prioridade.

## Responsabilidade

O `pizza-service` é responsável pelo catálogo de pizzas da OCI Pizza. Ele
gerencia nome, descrição, categoria, preço, disponibilidade e a imagem
associada a cada pizza.

O serviço não deve acessar diretamente dados de usuários, pedidos ou entrega.
Integrações com esses domínios devem ocorrer por contratos de API ou eventos
quando forem necessárias.

## Organização do código

- `routes/`: valida parâmetros, formulários multipart, autenticação e monta
  respostas JSend.
- `services/`: concentra as regras do catálogo, normalização dos textos,
  geração de nomes de imagens e coordenação da persistência e do storage.
- `repositories/`: encapsula a persistência das pizzas.
- `schemas/`: define contratos de criação, atualização e resposta.
- `models/`: representa o modelo interno da pizza e suas categorias.
- `dependencies/`: fornece autenticação, repositórios, unidade de trabalho e
  Object Storage.
- `services/objectstorage_service.py`: abstrai MinIO no desenvolvimento e OCI
  Object Storage fora desse ambiente.

As rotas não devem acessar repositórios ou clientes de storage diretamente nem
conter regras de negócio.

## Persistência

- O Oracle NoSQL é o provider primário e padrão.
- SQLAlchemy/MySQL permanece como provider alternativo suportado pelo serviço.
- A seleção ocorre por `PERSISTENCE_PROVIDER`; não misture providers na mesma
  execução.
- O acesso deve ocorrer pelos repositórios e pela unidade de trabalho fornecida
  por injeção de dependências.
- O `bootstrap.sh` garante a tabela, os dados de demonstração e o bucket nos
  providers selecionados por `NOSQL_PROVIDER` e `OBJECTSTORAGE_PROVIDER`.
  Execute-o somente para preparar um ambiente controlado.
- Alterações no modelo persistido devem ser refletidas nos providers
  suportados e no `README.md`.

## Autenticação e autorização

- Consultas públicas do catálogo podem ser realizadas sem access token.
- Criação, atualização e exclusão exigem access token JWT válido com
  `is_admin=true`.
- O serviço valida assinatura, emissor, audiência, expiração e `sub` do token
  usando o JWKS publicado pelo `user-service`.
- A claim `is_kitchen` não concede permissão para alterar o catálogo.
- Não duplique a validação de JWT dentro das rotas ou serviços.

## Imagens e Object Storage

- A criação exige um arquivo `image` não vazio com `Content-Type` iniciado por
  `image/`.
- `image_name` é opcional na criação e atualização. Quando omitido junto com
  um upload, o serviço deve gerar um nome único seguro, sem confiar no nome do
  arquivo enviado pelo cliente.
- O conteúdo deve ser enviado ao Object Storage com seu tipo MIME.
- Na atualização com nova imagem, a imagem anterior deve ser removida quando a
  chave do objeto mudar.
- Na exclusão, o registro e sua imagem associada devem ser removidos conforme
  o comportamento documentado do serviço.
- Para o provider `local`, utilize MinIO e as configurações locais. Para o
  provider `oci`, utilize OCI Object Storage com a estratégia definida por
  `OCI_AUTH_MODE`.
- Nunca registre conteúdo de imagem, credenciais ou URLs contendo informações
  sensíveis.

## Catálogo e valores

- Categorias válidas são `salgada`, `vegetariana` e `doce`.
- Preços devem ser tratados com `Decimal`, possuir valor positivo e ser
  serializados explicitamente nas respostas.
- Nome e descrição devem manter a normalização definida pelo serviço antes da
  persistência.
- Filtros de categoria, disponibilidade, limite e offset devem preservar o
  contrato existente da listagem.

## Validação futura de imagens

A validação atual verifica conteúdo e tipo MIME declarado. Não implemente uma
classificação semântica localmente. A integração com OCI Vision para confirmar
se a imagem representa uma pizza permanece um TODO e deve ser tratada como uma
alteração arquitetural documentada antes de sua implementação.

## Contratos e qualidade

- Preserve o padrão JSend e os códigos HTTP definidos nas rotas.
- Alterações em endpoints, campos, filtros, categorias, providers ou regras de
  upload devem ser refletidas no `README.md`.
- Não exponha detalhes internos de persistência, Object Storage ou autenticação
  nas respostas.
- Não crie diretórios ou arquivos de testes sem solicitação explícita.
- Preserve alterações existentes e execute apenas as validações pertinentes à
  alteração realizada.
