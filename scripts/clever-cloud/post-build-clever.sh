#! /bin/sh

PYTHONPATH=src uv run --no-dev src/infra/postgres/execute_migration.py
