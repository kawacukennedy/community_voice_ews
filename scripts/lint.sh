#!/usr/bin/env bash
# Lint all backend code
set -e
cd "$(dirname "$0")/../backend"
echo "=== flake8 ==="
flake8 app/ --max-line-length=120 --extend-ignore=E203 --count
echo "=== black ==="
black --check app/ --line-length=120
echo "All clean!"
