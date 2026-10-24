# Chaves SSH do Compute Firewall

Este diretório é reservado para o par de chaves SSH usado no acesso
administrativo às instâncias `compute-firewall`.

Os arquivos de chave são locais e não devem ser versionados. A chave privada
é utilizada pelo operador para abrir a sessão SSH. O Terraform lê
automaticamente o conteúdo de `firewall.pub` e envia somente a chave pública
para o metadata da instância.

Para gerar um novo par de chaves Ed25519 sem senha, execute na raiz do
repositório:

```bash
ssh-keygen -t ed25519 -N '' \
  -C 'oci-pizza-compute-firewall' \
  -f terraform/compute-firewall/keys/firewall
```

O comando cria:

- `firewall`: chave privada, que deve permanecer protegida;
- `firewall.pub`: chave pública, enviada para a instância pelo Terraform.

Não é necessário definir uma variável de ambiente para indicar o caminho da
chave. O caminho é configurado diretamente em `terraform/locals.tf`.
