#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

exec python3.8 -m http.server "$HTTP_PORT"