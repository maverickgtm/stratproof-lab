#!/usr/bin/env bash
set -euo pipefail

find . -type d -name "__pycache__" -prune -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
find . -type f -name ".DS_Store" -delete
find . -type f -name "*.sqlite" -delete
find . -type f -name "*.sqlite3" -delete
find . -type f -name "*.db" -delete

mkdir -p reports/stage35
{
  echo "STAGE35_CLEAN_BEFORE_GIT_UPLOAD=PASS"
  echo "DATE_UTC=$(date -u '+%Y-%m-%d %H:%M:%S UTC')"
  echo "PYC_COUNT=$(find . -type f -name '*.pyc' | wc -l | tr -d ' ')"
  echo "PYCACHE_COUNT=$(find . -type d -name '__pycache__' | wc -l | tr -d ' ')"
  echo "SQLITE_DB_COUNT=$(find . -type f \( -name '*.db' -o -name '*.sqlite' -o -name '*.sqlite3' \) | wc -l | tr -d ' ')"
} | tee reports/stage35/clean_before_git_upload.txt
