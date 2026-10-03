#!/bin/bash
set -e

# Ensure storage and staticfiles directories exist and are writable by appuser
for dir in /app/storage /app/staticfiles; do
    mkdir -p "$dir"
    chown -R appuser:appuser "$dir"
done

exec gosu appuser "$@"
