# OCI Pizza - Instruções do admin-service

Estas instruções complementam `services/AGENTS.md` e se aplicam somente ao
`admin-service`. Em caso de conflito, estas regras específicas têm prioridade.

## Responsabilidade

O `admin-service` é um BFF web para administradores e usuários da cozinha.
Ele apresenta a interface administrativa e coordena chamadas aos demais
serviços por meio de clientes HTTP. Não deve acessar bancos de dados nem
implementar regras de negócio pertencentes a outros serviços.

## Organização do código

- `routes/`: recebe requisições, valida formulários, chama os serviços e
  decide entre renderização ou redirecionamento.
- `services/`: concentra a orquestração dos casos de uso do painel.
- `clients/`: realiza a comunicação HTTP com os microsserviços; as rotas não
  devem chamar clientes diretamente.
- `forms/`: contém os formulários e suas validações.
- `templates/`: contém somente apresentação HTML e chamadas aos arquivos
  estáticos.
- `static/css/`, `static/js/` e `static/img/`: arquivos estáticos separados,
  preferencialmente organizados por área ou funcionalidade.

## Rotas e formulários

- Rotas `GET` que exibem páginas devem retornar `TemplateResponse`.
- Rotas que processam formulários devem obter os dados com
  `await request.form()` e instanciar o formulário no padrão do serviço:
  `form = UserLoginForm(await request.form())`.
- O formulário deve ser validado antes da chamada ao serviço.
- Rotas de submissão não devem retornar JSON nem renderizar novamente o
  formulário após o envio. Em sucesso ou falha, devem retornar
  `RedirectResponse` com status `303 See Other` e um código de mensagem na
  query string.
- A rota deve delegar a comunicação ao serviço; o serviço utiliza o cliente
  HTTP apropriado.
- Falhas esperadas de validação, autenticação ou comunicação devem ser
  convertidas em códigos de mensagem compreensíveis pela interface. Detalhes
  internos não devem ser expostos ao usuário.

## Autorização

- Rotas administrativas exigem `get_admin_authenticated_session`.
- Rotas da cozinha exigem `get_kitchen_authenticated_session`.
- O contexto da sessão deve ser obtido pela dependência de autenticação; não
  duplique a validação de tokens dentro das rotas.
- A interface deve respeitar a separação entre administradores e usuários da
  cozinha, inclusive nos menus e nas ações de pedidos.

## Templates e interação

- Templates não devem conter código Python nem regras de negócio.
- Ações destrutivas ou que alterem status devem solicitar confirmação por
  modal quando esse padrão já existir na interface.
- Operações que dependem de clientes HTTP devem utilizar o mecanismo de
  bloqueio de interação existente no `admin-service`, evitando submissões
  duplicadas.
- Formulários de criação e edição devem manter o padrão visual, os modais,
  máscaras e mensagens já utilizados no painel.

## Documentação e validação

- Atualize `README.md` quando forem alterados rotas, integrações, variáveis de
  ambiente ou comportamento do painel.
- Não crie diretórios ou arquivos de testes sem solicitação explícita.
- Preserve alterações existentes e execute apenas as validações disponíveis e
  pertinentes à alteração realizada.
