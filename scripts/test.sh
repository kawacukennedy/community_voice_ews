#!/usr/bin/env bash
# Run the full test suite
set -e
cd "$(dirname "$0")/../backend"
python -m pytest tests/ -v "$@"
