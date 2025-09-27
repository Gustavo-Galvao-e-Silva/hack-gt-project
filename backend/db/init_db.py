"""Initialize local PostgreSQL database by executing SQL from dbSchema.sql.

Usage:
  Set environment variables: PG_HOST, PG_PORT, PG_USER, PG_PASSWORD, PG_DB
  Or pass CLI args: --host, --port, --user, --password, --db

This script uses psycopg2 to connect and execute the SQL file.
"""
import os
import argparse
import sys
from pathlib import Path

try:
    import psycopg2
    from psycopg2 import sql
except Exception as e:
    print("psycopg2 is required. Install with: pip install psycopg2-binary")
    raise


DEFAULT_SQL_PATH = Path(__file__).parent / "dbSchema.sql"


def load_sql(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"SQL file not found: {path}")
    return path.read_text(encoding="utf-8")


from .connection import get_connection


def apply_sql(conn, sql_text: str):
    # Split statements carefully; psycopg2 can execute multi-statement SQL when using execute
    # inside a single transaction. We'll use executescript-like approach by splitting on ';' while
    # preserving dollar-quoted strings is more complex; but this schema is simple so split is safe.
    cur = conn.cursor()
    try:
        cur.execute(sql.SQL(sql_text))
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()


def parse_args():
    parser = argparse.ArgumentParser(description="Initialize PostgreSQL DB using dbSchema.sql")
    parser.add_argument("--host", default=os.getenv("PG_HOST", "localhost"))
    parser.add_argument("--port", default=os.getenv("PG_PORT", "5432"))
    parser.add_argument("--user", default=os.getenv("PG_USER", "postgres"))
    #change password as necessary
    parser.add_argument("--password", default=os.getenv("PG_PASSWORD", "password123"))
    parser.add_argument("--db", dest="dbname", default=os.getenv("PG_DB", "postgres"))
    parser.add_argument("--sql", dest="sql_path", default=str(DEFAULT_SQL_PATH))
    return parser.parse_args()


def main():
    args = parse_args()
    params = {
        "host": args.host,
        "port": args.port,
        "user": args.user,
        "password": args.password,
        "dbname": args.dbname,
    }

    sql_path = Path(args.sql_path)
    if not sql_path.is_absolute():
        # resolve relative to this file's directory
        sql_path = Path(__file__).parent / sql_path

    print(f"Using SQL file: {sql_path}")

    try:
        sql_text = load_sql(sql_path)
    except Exception as e:
        print(f"Failed to read SQL file: {e}")
        sys.exit(2)

    try:
        conn = get_connection(params)
    except Exception as e:
        print(f"Failed to connect to PostgreSQL: {e}")
        sys.exit(3)

    try:
        apply_sql(conn, sql_text)
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Failed to apply SQL: {e}")
        sys.exit(4)
    finally:
        try:
            conn.close()
        except Exception:
            pass


if __name__ == "__main__":
    main()
