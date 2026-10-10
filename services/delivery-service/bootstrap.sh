#!/bin/bash

#
# bootstrap.sh - delivery-service
#
# Este script prepara o ambiente de desenvolvimento local do delivery-service.
#
# Etapas executadas:
#
#  1. Cria o ambiente virtual Python, caso ainda não exista.
#  2. Ativa o ambiente virtual.
#  3. Atualiza o pip.
#  4. Instala as dependências definidas em requirements.txt.
#  5. Cria o arquivo .env local, caso ainda não exista.
#  6. Carrega as variáveis definidas no arquivo .env.
#  7. Identifica o provider de persistência configurado.
#  8. Cria a tabela de áreas de entrega no Oracle NoSQL.
#  9. Cadastra as áreas de entrega de Sorocaba no ambiente de desenvolvimento.
# 10. Finaliza o bootstrap deixando o serviço pronto para execução.
#
# Uso:
#
#     ./bootstrap.sh
#
# O script deve ser executado a partir do diretório raiz do delivery-service.
#

set -e

display_step() {
    local message="$1"
    local width=64
    local border
    local padding

    printf -v border '%*s' "$width" ''
    border=${border// /#}
    printf -v padding '%*s' "$((width - 4 - ${#message}))" ''

    echo
    echo "$border"
    echo "# $message$padding #"
    echo "$border"
    echo
}

VENV_DIR='.venv'
ENV_FILE='.env'

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

display_step 'Iniciando o bootstrap do delivery-service'

# Verifica se o script está sendo executado na raiz do delivery-service.
if [ ! -f 'requirements.txt' ]; then
    echo 'Erro: requirements.txt não encontrado.'
    echo 'Execute este script a partir do diretório raiz do delivery-service.'
    exit 1
fi

# Verifica se o Python 3.11 está disponível.
if ! command -v python3.11 >/dev/null 2>&1; then
    echo 'Erro: Python 3.11 não foi encontrado.'
    exit 1
fi

display_step 'Preparando o ambiente virtual Python'

if [ ! -d "$VENV_DIR" ]; then
    echo 'Criando ambiente virtual Python...'
    python3.11 -m venv "$VENV_DIR"
else
    echo 'Ambiente virtual Python já existe.'
fi

# Ativa o ambiente virtual Python.
source "$VENV_DIR/bin/activate"

display_step 'Atualizando o pip'
python -m pip install --upgrade pip

display_step 'Instalando as dependências Python'
python -m pip install --no-cache-dir -r requirements.txt

display_step 'Configurando o arquivo .env do ambiente local'

if [ ! -f "$ENV_FILE" ]; then
    echo 'Criando arquivo .env para desenvolvimento local...'

    cat > "$ENV_FILE" <<'EOF'
APP_NAME=delivery-service
APP_ENV=development
DEBUG=true

# Persistência
PERSISTENCE_PROVIDER=nosql

# Oracle NoSQL
NOSQL_TABLE_NAME=delivery_areas
NOSQL_ENDPOINT=http://localhost:18080

# JWT
JWT_ISSUER=user-service
JWT_AUDIENCE=oci-pizza
JWT_JWKS_URL=http://localhost:8002/.well-known/jwks.json

# Logging
LOG_LEVEL=INFO
OCI_LOG_ID=
EOF

else
    echo 'Arquivo .env já existe.'
fi

# Carrega as variáveis do arquivo .env no ambiente do processo atual.
echo 'Carregando configurações do ambiente...'

set -a
source "$ENV_FILE"
set +a

display_step 'Inicialização da persistência'

echo "Provider de persistência configurado: ${PERSISTENCE_PROVIDER}"

if [ "${PERSISTENCE_PROVIDER}" != 'nosql' ]; then
    echo "Provider de persistência não suportado pelo bootstrap: ${PERSISTENCE_PROVIDER}"
    exit 1
fi

echo 'Inicializando persistência Oracle NoSQL...'

python <<'PYTHON'
import os

from borneo import TableRequest

from app.repositories.nosql.connection import get_nosql_handle


table_name = os.getenv(
    'NOSQL_TABLE_NAME',
    'delivery_areas'
)

handle = get_nosql_handle()

statement = f'''
    CREATE TABLE IF NOT EXISTS {table_name} (
        id STRING,
        name STRING,
        zip_code_start STRING,
        zip_code_end STRING,
        delivery_fee NUMBER,
        estimated_minutes INTEGER,
        active BOOLEAN,
        created_at TIMESTAMP(3),
        updated_at TIMESTAMP(3),
        PRIMARY KEY (id)
    )
'''

print(f'Criando tabela {table_name}, caso ainda não exista...')

request = TableRequest().set_statement(statement)
result = handle.table_request(request)
result.wait_for_completion(handle, 60000, 1000)

print(f'Tabela {table_name} pronta para utilização.')

handle.close()
PYTHON

# Os dados de demonstração são criados somente no ambiente local.
if [ "${APP_ENV}" = 'development' ]; then
    display_step 'Criando áreas de entrega de demonstração'

    python <<'PYTHON'
import csv

from datetime import datetime, timezone
from decimal import Decimal
from io import StringIO
from uuid import NAMESPACE_URL, uuid5

from app.dependencies.database import get_delivery_area_repository
from app.models.delivery_area import DeliveryArea


# As faixas abaixo correspondem aos dados de entrega de Sorocaba utilizados
# no ambiente de desenvolvimento. Mantê-las no bootstrap torna a preparação
# do ambiente independente de arquivos externos de seed.
DELIVERY_AREAS_CSV = '''zip_code_start,zip_code_end,delivery_fee,estimated_minutes,active
18000001,18003999,5.0,30,True
18004000,18007999,7.0,35,False
18008000,18011999,6.5,30,True
18012000,18015999,8.0,40,False
18016000,18019999,7.5,35,False
18020000,18023999,9.0,40,False
18024000,18027999,10.0,45,True
18028000,18031999,8.5,40,True
18032000,18035999,11.0,45,True
18036000,18039999,9.5,40,True
18040000,18043999,12.0,50,True
18044000,18047999,10.5,45,True
18048000,18051999,13.0,50,True
18052000,18055999,11.5,45,False
18056000,18059999,14.0,55,False
18060000,18063999,12.5,50,True
18064000,18067999,15.0,55,True
18068000,18071999,13.5,50,True
18072000,18075999,16.0,60,True
18076000,18079999,14.5,55,True
18080000,18083999,17.0,60,True
18084000,18087999,15.5,55,False
18088000,18091999,18.0,65,False
18092000,18095999,16.5,60,True
18096000,18099999,19.0,65,True
18100000,18101999,17.5,60,True
18102000,18103999,20.0,70,True
18104000,18105999,18.5,65,False
18106000,18107999,21.0,70,True
18108000,18109999,22.0,75,True
'''

repository = get_delivery_area_repository()
created_at = datetime.now(timezone.utc)

for position, row in enumerate(
    csv.DictReader(StringIO(DELIVERY_AREAS_CSV)),
    start=1
):
    zip_code_start = row['zip_code_start']
    zip_code_end = row['zip_code_end']

    # O UUID determinístico permite executar o bootstrap repetidas vezes sem
    # cadastrar novamente uma faixa que já esteja presente na tabela.
    delivery_area_id = uuid5(
        NAMESPACE_URL,
        f'ocipizza:delivery-area:{zip_code_start}:{zip_code_end}'
    )

    if repository.get_by_id(delivery_area_id) is not None:
        print(
            'Área de entrega já existe: '
            f'{zip_code_start} a {zip_code_end}'
        )
        continue

    delivery_area = DeliveryArea(
        id=delivery_area_id,
        name=f'Área de entrega Sorocaba {position:02d}',
        zip_code_start=zip_code_start,
        zip_code_end=zip_code_end,
        delivery_fee=Decimal(row['delivery_fee']),
        estimated_minutes=int(row['estimated_minutes']),
        active=row['active'].lower() == 'true',
        created_at=created_at,
        updated_at=created_at
    )

    repository.create(delivery_area)

    print(
        'Área de entrega criada: '
        f'{zip_code_start} a {zip_code_end}'
    )

# O repositório NoSQL mantém o handle aberto durante todas as inclusões.
repository.handle.close()
PYTHON
fi

display_step 'Bootstrap do delivery-service concluído com sucesso'

exit 0
