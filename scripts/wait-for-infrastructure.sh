#!/bin/bash

echo "Waiting Oracle NoSQL..."

until curl -s http://localhost:18080 >/dev/null
do
    sleep 5
done

echo "Oracle NoSQL ready"

echo "Waiting Object Storage..."

until curl -s http://localhost:9000/minio/health/live >/dev/null
do
    sleep 5
done

echo "Object Storage ready"

exit 0
