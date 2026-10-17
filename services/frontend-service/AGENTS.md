# OCI Pizza - Instruções do frontend-service

Estas instruções complementam `services/AGENTS.md` e se aplicam somente ao
`frontend-service`. Em caso de conflito, estas regras específicas têm prioridade.

## Responsabilidade

O `frontend-service` é um BFF web da OCI Pizza. Ele renderiza a interface para
o navegador e intermedeia as chamadas aos microsserviços. O navegador não deve
acessar diretamente os serviços internos nem receber access tokens ou refresh
tokens.

O serviço não deve acessar bancos de dados dos microsserviços nem duplicar
regras de negócio de catálogo, usuários, entrega ou pedidos.

## Organização do código

- `routes/`: recebe requisições web, valida formulários, chama serviços e
  renderiza páginas ou redireciona.
- `services/`: orquestra os casos de uso do BFF e coordena clientes e sessão.
- `clients/`: realiza chamadas HTTP aos microsserviços; rotas não devem chamar
  clientes diretamente.
- `forms/`: contém formulários WTForms e validações de entrada.
- `templates/`: contém apenas apresentação Jinja2.
- `static/css/`, `static/js/` e `static/img/`: arquivos estáticos separados,
  organizados por área ou funcionalidade quando necessário.

## Rotas e formulários

- Rotas `GET` que exibem páginas devem retornar `TemplateResponse`.
- Rotas de submissão devem obter os dados com `await request.form()` e criar o
  formulário no padrão do serviço, por exemplo:
  `form = UserLoginForm(await request.form())`.
- O formulário deve ser validado antes de chamar qualquer serviço ou cliente.
- Após qualquer submissão, tanto em sucesso quanto em falha, a rota deve
  retornar `RedirectResponse` com status `303 See Other` para impedir o reenvio
  do formulário ao atualizar a página.
- Rotas web não devem retornar JSON ao navegador. Mensagens funcionais devem
  ser transportadas por códigos na query string e exibidas pelo componente de
  mensagens da interface.
- Erros esperados devem ser convertidos em códigos de mensagem sem expor
  detalhes internos, tokens ou credenciais.

## Sessão, autenticação e segurança

- Access tokens e refresh tokens devem permanecer no armazenamento de sessão
  do backend; o navegador recebe somente o identificador opaco da sessão em
  cookie `HttpOnly`.
- Use as dependências de sessão e autenticação existentes; não replique a
  validação de JWT nas rotas.
- Formulários que alteram estado devem manter a proteção CSRF configurada no
  serviço.
- Logout deve remover a sessão local, apagar o cookie e revogar a sessão
  remota quando essa operação estiver disponível.
- Nunca registre ou exiba tokens, senhas, cookies ou outros segredos.

## Integração com microsserviços

- Toda comunicação com `user-service`, `pizza-service`, `delivery-service` e
  `order-service` deve passar pelo cliente e serviço correspondentes.
- Preserve os contratos HTTP existentes, incluindo métodos, payloads, códigos
  de erro e respostas JSend dos microsserviços.
- O checkout deve revalidar os dados recebidos das APIs antes de criar o
  pedido; valores mantidos no navegador não são fonte de verdade.
- Falhas de comunicação devem produzir uma mensagem amigável e um redirect,
  sem retornar traceback ou resposta técnica ao usuário.

## Templates e JavaScript

- Templates não devem conter código Python nem regras de negócio.
- Operações que dependem de chamadas HTTP devem utilizar o mecanismo de
  bloqueio de interação existente, evitando submissões duplicadas.
- Validações simples de experiência do usuário podem existir em JavaScript,
  mas a validação definitiva deve permanecer no formulário e no serviço de
  destino.
- Ações destrutivas ou irreversíveis devem solicitar confirmação por modal
  quando esse padrão existir na interface.
- Mantenha CSS, JavaScript e imagens em seus diretórios estáticos; não crie
  estilos ou scripts inline sem necessidade justificada.

## Documentação e qualidade

- Atualize `README.md` quando forem alterados rotas, integrações, sessões,
  variáveis de ambiente ou comportamento da interface.
- Não crie diretórios ou arquivos de testes sem solicitação explícita.
- Preserve alterações existentes e execute apenas as validações pertinentes à
  alteração realizada.
