# Como criar um par de chaves SSH

Entre no diretório usado pelo Terraform:

~~~bash
cd $HOME/ocn-ocipizza/terraform/ssh-keys
~~~

Crie um par para os Compute Firewalls e outro para os worker nodes do OKE:

~~~bash
ssh-keygen -t ed25519 -a 100 -f firewall -C "ocipizza-firewall"
ssh-keygen -t ed25519 -a 100 -f worker-nodes -C "ocipizza-worker-nodes"
~~~

Cada comando solicitará:

1. Uma senha opcional para proteger a chave privada.
2. A confirmação da senha, quando informada.

Ao final, serão criados dois arquivos:

- a chave privada, que deve permanecer protegida e nunca deve ser compartilhada;
- a chave pública, identificada pela extensão `.pub`, que pode ser instalada nos recursos que aceitarão conexões SSH.

Restrinja as permissões da chave privada:

~~~bash
chmod 0400 firewall worker-nodes
~~~

Para conferir a chave pública:

~~~bash
ssh-keygen -y -f firewall
ssh-keygen -y -f worker-nodes
~~~

O conteúdo exibido deve corresponder ao conteúdo do arquivo público gerado.

O Terraform não lê esses arquivos diretamente. Antes do `terraform plan` ou
`terraform apply`, carregue somente as chaves públicas nas variáveis:

~~~bash
export TF_VAR_firewall_ssh_public_key="$(cat $HOME/ocn-ocipizza/terraform/ssh-keys/firewall.pub)"
export TF_VAR_oke_worker_ssh_public_key="$(cat $HOME/ocn-ocipizza/terraform/ssh-keys/worker-nodes.pub)"
~~~
