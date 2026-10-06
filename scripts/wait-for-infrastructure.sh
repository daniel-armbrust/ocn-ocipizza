#!/bin/bash

echo "Aguardando Oracle NoSQL..."

until curl -s http://localhost:18080 >/dev/null
do
    echo "Oracle NoSQL ainda não está disponível. Tentando novamente..."
    sleep 5
done

echo "Oracle NoSQL disponível"

echo "Aguardando MySQL..."

until timeout 1 bash -c "</dev/tcp/localhost/13306" 2>/dev/null
do
    echo "MySQL ainda não está disponível. Tentando novamente..."
    sleep 5
done

echo "MySQL disponível"

echo "Aguardando RabbitMQ..."

until timeout 1 bash -c "</dev/tcp/localhost/5672" 2>/dev/null
do
    echo "RabbitMQ ainda não está disponível. Tentando novamente..."
    sleep 5
done

echo "RabbitMQ disponível"

echo "Aguardando Redis..."

until redis-cli -h localhost -p 16379 ping 2>/dev/null | grep -q "PONG"
do
    echo "Redis ainda não está disponível. Tentando novamente..."
    sleep 2
done

echo "Redis disponível."

exit 0
