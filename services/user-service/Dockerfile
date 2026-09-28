#
# user-service/Dockerfile
#
FROM container-registry.oracle.com/os/oraclelinux:8-slim

# Evita a criação de arquivos .pyc e força saída de logs sem buffering.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Instala Python 3 e pip.
RUN microdnf install -y python3.11 python3.11-pip \
    && ln -s /usr/bin/python3.11 /usr/local/bin/python \
    && ln -s /usr/bin/python3.11 /usr/local/bin/python3 \
    && microdnf clean all

# Diretório de trabalho da aplicação.
WORKDIR /app

# Copia primeiro as dependências para aproveitar o cache do Docker.
COPY requirements.txt .

# Atualiza o pip e instala as dependências Python.
RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação.
COPY . .

# Porta interna utilizada pelo FastAPI/Uvicorn.
EXPOSE 8000

# Inicia a aplicação FastAPI.
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]