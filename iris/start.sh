#!/bin/bash
set -e

echo "Starting Unity Catalog Server on port 8081..."
cd /home/unitycatalog
UC_SERVER_PORT=8081 UC_SERVER_HOST=0.0.0.0 ./bin/start-uc-server &
UC_PID=$!

echo "Starting nginx on port 8080..."
nginx -g 'daemon off;' &
NGINX_PID=$!

echo "Services started. UC PID: $UC_PID, Nginx PID: $NGINX_PID"

# Simple health check loop
while true; do
    sleep 30
    if ! kill -0 $UC_PID 2>/dev/null; then
        echo "UC server died, exiting..."
        exit 1
    fi
    if ! kill -0 $NGINX_PID 2>/dev/null; then
        echo "Nginx died, exiting..."
        exit 1
    fi
done
