FROM container-registry.oracle.com/os/oraclelinux:8-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV ENVIRONMENT=production

RUN microdnf update -y \
    && microdnf install -y \
        python3.11 \
        python3.11-pip \
        shadow-utils \
    && microdnf clean all

RUN alternatives \
    --set python /usr/bin/python3.11

COPY requirements.txt .

RUN python -m pip install \
    --no-cache-dir \
    --upgrade pip \
    && python -m pip install \
    --no-cache-dir \
    -r requirements.txt

RUN useradd --create-home appuser

RUN mkdir -p /home/appuser/.oci \
    && chown -R appuser:appuser /home/appuser/.oci

COPY --chown=appuser:appuser app/ ./app/

USER appuser

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
