#
# user-service/Dockerfile
#
FROM container-registry.oracle.com/os/oraclelinux:8-slim

ARG APP_UID=1000
ARG APP_GID=1000

# Evita a criação de arquivos .pyc e força saída de logs sem buffering.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Instala Python 3, pip e os utilitários para criação do usuário da aplicação.
RUN microdnf install -y python3.11 python3.11-pip shadow-utils \
    && ln -s /usr/bin/python3.11 /usr/local/bin/python \
    && ln -s /usr/bin/python3.11 /usr/local/bin/python3 \
    && groupadd --gid "$APP_GID" app \
    && useradd \
        --uid "$APP_UID" \
        --gid "$APP_GID" \
        --home-dir /app \
        --no-create-home \
        --shell /sbin/nologin \
        app \
    && microdnf clean all

# Diretório de trabalho da aplicação.
WORKDIR /app

# Copia primeiro as dependências para aproveitar o cache do Docker.
COPY requirements.txt .

# Atualiza o pip e instala as dependências Python.
RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir -r requirements.txt

# Copia o código e transfere sua propriedade ao usuário da aplicação.
COPY --chown=app:app . .

# Executa a aplicação sem privilégios de root. O UID/GID padrão 1000 também
# permite ler as chaves JWT locais montadas pelo Docker Compose.
USER app:app

# Porta interna utilizada pelo FastAPI/Uvicorn.
EXPOSE 8000

# Inicia a aplicação FastAPI.
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
