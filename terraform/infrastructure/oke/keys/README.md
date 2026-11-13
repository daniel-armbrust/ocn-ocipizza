# Chaves SSH dos Worker Nodes

Este diretório é reservado para o par de chaves SSH usado no acesso
administrativo às instâncias dos Worker Nodes.

Os arquivos de chave são locais e não devem ser versionados. A chave privada
é utilizada pelo operador para abrir a sessão SSH. O conteúdo de
`worker-nodes.pub` deve ser fornecido ao Resource Manager pela variável
`oke_worker_ssh_public_key`; somente a chave pública é enviada ao metadata.

Para gerar um novo par de chaves Ed25519 sem senha, execute na raiz do
repositório:

```bash
ssh-keygen -t ed25519 -N '' \
  -C 'ocipizza-worker-nodes' \
  -f terraform/infrastructure/oke/keys/worker-nodes
```

O comando cria:

- `worker-nodes`: chave privada, que deve permanecer protegida;
- `worker-nodes.pub`: chave pública, enviada para a instância pelo Terraform.

Não envie a chave privada ao Resource Manager. Em execuções locais, a chave
pública pode ser informada por `TF_VAR_oke_worker_ssh_public_key`.
