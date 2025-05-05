#
# Dockerfile
#
FROM container-registry.oracle.com/os/oraclelinux:8-slim

LABEL maintainer="Daniel Armbrust <darmbrust@gmail.com>"

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV STATIC_URL=/static
ENV STATIC_PATH=/home/ocipizza/app/static

COPY requirements.txt ./
COPY docker-entrypoint.sh ./

RUN microdnf update -y && \
    microdnf install -y gcc python38-devel python3.8 && \
    python -m ensurepip && \
    python -m pip install --no-cache-dir --upgrade pip setuptools && \
    python -m pip install --no-cache-dir -r requirements.txt && \
    microdnf clean all && rm -rf /var/cache/yum

RUN adduser -l -d /home/ocipizza -m webapp

COPY --chown=webapp:webapp ./ocipizza /home/ocipizza/

USER webapp
EXPOSE 5000

ENTRYPOINT ["./docker-entrypoint.sh"]