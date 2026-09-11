# OCI Pizza

Aplicação cloud-native de referência para demonstrar desenvolvimento de aplicações modernas na OCI, microsserviços, containers, Kubernetes, IaC e CI/CD.

## Desenvolvimento local

O ambiente local utiliza Docker Compose e os comandos definidos no `Makefile`.

Para subir somente a infraestrutura local:

```bash
docker compose up -d nosql object-storage
```

Ou usando o Makefile:

```bash
make development-infra
```

Para executar o seed após a infraestrutura estar disponível:

```bash
docker compose run --rm seed
```

Ou usando o Makefile:

```bash
make development-seed
```

Para subir infraestrutura, executar seed e iniciar os serviços da aplicação em sequência:

```bash
make development-up
```

Esse alvo executa:

1. `development-infra`
2. `development-seed`
3. `development-services`

Para construir as imagens normalmente:

```bash
make build
```

Para reconstruir as imagens sem cache:

```bash
make force-build
make development-up
```

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

Para executar os testes automatizados:

```bash
make test
```

Para acompanhar os logs:

```bash
make development-logs
```

Para parar o ambiente:

```bash
make development-down
```
