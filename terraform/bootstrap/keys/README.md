# Como criar um par de chaves SSH

Para criar um novo par de chaves SSH Ed25519, execute:

~~~bash
ssh-keygen -t ed25519 -a 100
~~~

O comando solicitará:

1. O caminho onde o par de chaves será armazenado.
2. Uma senha opcional para proteger a chave privada.
3. A confirmação da senha, quando informada.

Ao final, serão criados dois arquivos:

- a chave privada, que deve permanecer protegida e nunca deve ser compartilhada;
- a chave pública, identificada pela extensão `.pub`, que pode ser instalada nos recursos que aceitarão conexões SSH.

Restrinja as permissões da chave privada:

~~~bash
chmod 0400 caminho-da-chave-privada
~~~

Para conferir a chave pública:

~~~bash
ssh-keygen -y -f caminho-da-chave-privada
~~~

O conteúdo exibido deve corresponder ao conteúdo do arquivo público gerado.
