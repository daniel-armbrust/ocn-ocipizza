#
# Dockerfile
#
FROM container-registry.oracle.com/os/oraclelinux:8-slim

LABEL maintainer="Daniel Armbrust <darmbrust@gmail.com>"

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /smtpd

COPY ./smtp-server.py ./
COPY ./docker-entrypoint.sh ./

RUN microdnf install -y python3.8 && \
    microdnf clean all && rm -rf /var/cache/yum

ENTRYPOINT ["./docker-entrypoint.sh"]