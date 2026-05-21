#!/usr/bin/env bash
set -euo pipefail

echo "Cleaning Python cache files before Git upload..."
find . -type d -name "__pycache__" -prune -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
find . -type f -name ".DS_Store" -delete

echo "Running final public checks..."
python3 tests/smoke_test_public_package.py
python3 scripts/stage22_final_github_preflight.py

echo "STAGE34_CLEAN_BEFORE_GIT_UPLOAD=PASS"
