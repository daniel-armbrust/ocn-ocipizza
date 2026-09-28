#!/bin/bash

echo "Waiting Oracle NoSQL..."

until curl -s http://localhost:18080 >/dev/null
do
    sleep 5
done

echo "Oracle NoSQL ready"

echo "Waiting MySQL..."

until timeout 1 bash -c "</dev/tcp/localhost/13306" 2>/dev/null
do
    sleep 5
done

echo "MySQL ready"

echo "Waiting RabbitMQ..."

until timeout 1 bash -c "</dev/tcp/localhost/5672" 2>/dev/null
do
    sleep 5
done

echo "RabbitMQ ready"

exit 0
