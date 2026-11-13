# Chaves SSH do Compute Firewall

Este diretório é reservado para o par de chaves SSH usado no acesso
administrativo às instâncias `compute-firewall`.

Os arquivos de chave são locais e não devem ser versionados. A chave privada
é utilizada pelo operador para abrir a sessão SSH. O conteúdo de `firewall.pub`
deve ser fornecido ao Resource Manager pela variável
`firewall_ssh_public_key`; somente a chave pública é enviada ao metadata.

Para gerar um novo par de chaves Ed25519 sem senha, execute na raiz do
repositório:

```bash
ssh-keygen -t ed25519 -N '' \
  -C 'ocipizza-compute-firewall' \
  -f terraform/infrastructure/compute-firewall/keys/firewall
```

O comando cria:

- `firewall`: chave privada, que deve permanecer protegida;
- `firewall.pub`: chave pública, enviada para a instância pelo Terraform.

Não envie a chave privada ao Resource Manager. Em execuções locais, a chave
pública pode ser informada por `TF_VAR_firewall_ssh_public_key`.
