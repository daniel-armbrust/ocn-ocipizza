# OCI Pizza

Aplicação cloud-native de referência para demonstrar desenvolvimento de aplicações modernas na OCI, microsserviços, containers, Kubernetes, IaC e CI/CD.

## Desenvolvimento local

O ambiente local utiliza Docker Compose e os alvos definidos no `Makefile`.
Esses alvos separam a infraestrutura, o bootstrap dos dados e os serviços da
aplicação.

Para listar os alvos disponíveis e suas descrições:

```bash
make help
```

O alvo `help` é o padrão e também será executado quando `make` for chamado sem
argumentos.

### Iniciar o ambiente

Para iniciar a infraestrutura, aguardar sua disponibilidade e subir todos os
serviços da aplicação:

```bash
make development
```

Para iniciar e validar apenas os componentes de infraestrutura:

```bash
make development-infra
```

Para iniciar apenas os serviços da aplicação, quando a infraestrutura já
estiver disponível:

```bash
make development-services
```

### Bootstrap dos serviços

O bootstrap inicia e valida a infraestrutura e, em seguida, executa todos os
arquivos `services/*/bootstrap.sh` encontrados no repositório:

```bash
make development-bootstrap
```

Atualmente, possuem bootstrap os serviços `delivery-service`, `order-service`,
`pizza-service` e `user-service`. Cada script é executado a partir da raiz do
respectivo serviço.

> **Atenção:** os scripts de bootstrap preparam o ambiente local e podem
> recriar tabelas e dados de demonstração. Use esse alvo somente quando essa
> reinicialização for desejada.

Após o bootstrap, inicie os serviços com:

```bash
make development-services
```

### Construção das imagens

Para construir somente as imagens dos serviços da aplicação, utilizando o
cache disponível:

```bash
make build
```

Para reconstruir somente essas imagens, sem utilizar cache:

```bash
make rebuild
```

Para reconstruir os serviços sem cache e depois iniciar o ambiente completo:

```bash
make development-rebuild
```

Os alvos de construção não incluem MySQL, Oracle NoSQL, RabbitMQ, Redis,
Object Storage ou Mailpit.

### Logs e encerramento

Para acompanhar os logs dos serviços da aplicação:

```bash
make development-logs
```

Para parar e remover os containers e a rede do ambiente, preservando os
volumes:

```bash
make development-down
```

### Qualidade e CI/CD

<!-- TODO: Documentar e disponibilizar o alvo de lint dos serviços. -->
<!-- TODO: Documentar e disponibilizar o alvo de testes automatizados. -->
<!-- TODO: Documentar os alvos compartilhados com os pipelines de CI/CD. -->

Os comandos de lint, testes automatizados e CI/CD ainda serão implementados.

## Testando o pizza-service

Com o ambiente iniciado, o `pizza-service` fica disponível no host em:

```text
http://localhost:8001
```

Para testar o health check:

```bash
curl -i http://localhost:8001/health
```

Para listar pizzas:

```bash
curl -i http://localhost:8001/pizzas
```

Para consultar uma pizza específica:

```bash
curl -i http://localhost:8001/pizzas/1
```

Para criar uma pizza usando o token administrativo local:

```bash
curl -i -X POST http://localhost:8001/pizzas \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer admin-token" \
  -d '{
    "name": "Teste",
    "description": "Pizza de teste",
    "category": "tradicional",
    "price": 49.9,
    "image_name": "teste.jpg",
    "available": true
  }'
```
