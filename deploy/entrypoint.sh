#!/usr/bin/env bash
set -e

uv run flask --app src/main --debug run --host 0.0.0.0 --port 8080 &
BACK_PID=$!

term() { kill -TERM "$BACK_PID" 2>/dev/null || true; }
trap term SIGTERM SIGINT

nginx -g 'daemon off;' &
NGINX_PID=$!

wait -n "$BACK_PID" "$NGINX_PID"
term
kill -TERM "$NGINX_PID" 2>/dev/null || true
wait || true
