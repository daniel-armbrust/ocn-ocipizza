#
# Dockerfile
#
FROM container-registry.oracle.com/os/oraclelinux:8-slim

LABEL maintainer="Daniel Armbrust <darmbrust@gmail.com>"

ENV CLODSIM_TAR_FILE="oracle-nosql-cloud-simulator-5.11.6.tar.gz"
ENV CLOUDSIM_DIR="/cloudsim/oracle-nosql-cloud-simulator-5.11.6"

WORKDIR /

ADD ./cloudsim/oracle-nosql-cloud-simulator-5.11.6.tar.gz ./cloudsim
COPY docker-entrypoint.sh ./

RUN microdnf update -y && \
    microdnf install -y java-11-openjdk && \ 
    microdnf clean all && rm -rf /var/cache/yum

EXPOSE 8080

ENTRYPOINT ["./docker-entrypoint.sh"]