#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

cd $CLOUDSIM_DIR

exec sh runCloudSim -root ./ocipizza -host "$NOSQL_CLOUDSIM_IP" -httpPort "$NOSQL_CLOUDSIM_PORT" -verbose