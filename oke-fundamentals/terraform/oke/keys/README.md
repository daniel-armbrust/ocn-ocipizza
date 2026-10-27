# Chaves SSH dos Worker Nodes

Este diretório é reservado para o par de chaves SSH usado no acesso
administrativo às instâncias dos Worker Nodes.

Os arquivos de chave são locais e não devem ser versionados. A chave privada
é utilizada pelo operador para abrir a sessão SSH. O Terraform lê
automaticamente o conteúdo de `worker-nodes.pub` e envia somente a chave pública
para o metadata da instância.

Para gerar um novo par de chaves Ed25519 sem senha, execute na raiz do
repositório:

```bash
ssh-keygen -t ed25519 -N '' \
  -C 'ocipizza-worker-nodes' \
  -f oke-fundamentals/terraform/oke/keys/worker-nodes
```

O comando cria:

- `worker-nodes`: chave privada, que deve permanecer protegida;
- `worker-nodes.pub`: chave pública, enviada para a instância pelo Terraform.

Não é necessário definir variável ou indicar o caminho da chave. O módulo lê
automaticamente `keys/worker-nodes.pub` na configuração de `oke/locals.tf`.
