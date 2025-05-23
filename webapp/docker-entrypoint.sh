#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

WEBAPP_HOME="/home/ocipizza"

cd "$WEBAPP_HOME"

if [ "$FLASK_ENV" == "production" ]; then
    # How Many Workers?
    # https://docs.gunicorn.org/en/latest/design.html#how-many-workers
    workers_count=$((2 * $(grep -c ^processor /proc/cpuinfo) + 1))
    
    export FLASK_APP="wsgi.py"

    exec gunicorn -w "$workers_count" -b 0.0.0.0:5000 wsgi:app \
                  --access-logfile - \
                  --error-logfile - \
                  --timeout 0
else
    flask run --debug --reload --host=0.0.0.0
fi