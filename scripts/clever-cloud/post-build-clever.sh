#! /bin/sh

PYTHONPATH=src uv run src/infra/postgres/execute_migration.py
