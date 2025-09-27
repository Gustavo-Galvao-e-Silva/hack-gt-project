"""Centralized PostgreSQL connection helpers.

Provides helpers to build connection params from environment, obtain a psycopg2
connection, and optionally create a connection pool in the future.
"""
from typing import Dict, Optional
import os

try:
    import psycopg2
except Exception:
    raise


def get_params_from_env() -> Dict[str, str]:
    return dict(
        host=os.getenv("PG_HOST", "localhost"),
        port=os.getenv("PG_PORT", "5432"),
        user=os.getenv("PG_USER", "postgres"),
        password=os.getenv("PG_PASSWORD", "password123"),
        dbname=os.getenv("PG_DB", "postgres"),
    )


def get_connection(params: Optional[Dict[str, str]] = None):
    """Return a new psycopg2 connection.

    If params is None, build params from environment variables.
    """
    actual_params = params if params is not None else get_params_from_env()
    return psycopg2.connect(**actual_params)


def get_connection_from_env():
    """Convenience wrapper that always uses environment variables."""
    return get_connection(get_params_from_env())
