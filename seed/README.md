# Seed

Este diretório contém scripts e dados utilizados para inicialização de ambientes da aplicação OCI Pizza.

O seed carrega:

- Tabela e dados do catálogo de pizzas no Oracle NoSQL
- Imagens das pizzas no Object Storage compatível com S3 em desenvolvimento local

O seed é destrutivo para os recursos que gerencia: a cada execução ele remove e recria a tabela de pizzas no Oracle NoSQL, remove e recria o bucket de imagens no Object Storage local e insere novamente os dados iniciais.

## Desenvolvimento local

No ambiente local, o fluxo esperado é:

```bash
make development-infra
make development-seed
```

O comando `make development-infra` sobe os serviços de infraestrutura definidos no `docker-compose.yaml`, incluindo Oracle NoSQL e MinIO.

O comando `make development-seed` executa o serviço `seed` definido no `docker-compose.yaml`. Esse serviço instala as dependências de `seed/requirements.txt`, aguarda Oracle NoSQL e MinIO ficarem disponíveis, executa `seed/run-seed.py` e finaliza.

Também é possível executar diretamente:

```bash
docker compose run --rm seed
```

Variáveis principais em desenvolvimento:

```bash
ENVIRONMENT=development
OCI_REGION=sa-saopaulo-1
OCI_NOSQL_ENDPOINT=http://localhost:18080
OCI_NOSQL_TABLE=pizzas
OBJECT_STORAGE_ENDPOINT=http://localhost:9000
OBJECT_STORAGE_BUCKET=pizza-images
OBJECT_STORAGE_ACCESS_KEY=minioadmin
OBJECT_STORAGE_SECRET_KEY=minioadmin
```

Em desenvolvimento, o seed usa `borneo` para conectar ao Oracle NoSQL local/proxy e `minio` para enviar imagens ao MinIO.

## Produção em OCI

Em produção, o seed deve ser executado dentro de um recurso OCI autorizado por Instance Principal, como uma Compute Instance operacional ou uma carga controlada em ambiente OCI equivalente.

Variáveis principais em produção:

```bash
ENVIRONMENT=production
OCI_REGION=sa-saopaulo-1
OCI_NOSQL_TABLE=pizzas
OCI_NOSQL_COMPARTMENT_ID=ocid1.compartment.oc1...
```

Para Oracle NoSQL, o seed usa Instance Principal por meio de:

```python
SignatureProvider.create_with_instance_principal(region=region)
```

O compartment deve ser informado por `OCI_NOSQL_COMPARTMENT_ID`, pois Instance Principal exige compartment explícito para operações no Oracle NoSQL Cloud Service.

## Observação sobre Object Storage

Atualmente, o upload de imagens usa cliente compatível com S3 (`minio`), adequado ao ambiente local com MinIO.

Para produção em OCI Object Storage real, o fluxo recomendado é substituir o upload por `oci.object_storage.ObjectStorageClient` usando Instance Principal, evitando credenciais estáticas.

## Dados de pizzas

Os dados ficam em:

```text
seed/pizzas/pizzas.jsonl
```

Durante a carga, os registros são normalizados para o contrato do `pizza-service`, incluindo:

- `id` numérico, como `1`
- `category`
- `available`
- `created_at`
- `updated_at`

As imagens ficam em:

```text
seed/pizzas/img/
```
