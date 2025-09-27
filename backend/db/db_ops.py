"""Database helper operations for nodes, users, and workspaces.

Provides add_* and delete_* functions using psycopg2 parameterized queries.
Each add_* returns the newly inserted row as a dict. Each delete_* returns True if a row was deleted.

Usage: import the functions and pass an existing psycopg2 connection or use get_connection_from_env().
"""
from typing import Optional, Dict, Any, List
from pathlib import Path
import os

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    from psycopg2 import sql
except Exception:
    raise

from .connection import get_connection_from_env


def _row_from_cursor(cur) -> Optional[Dict[str, Any]]:
    row = cur.fetchone()
    if not row:
        return None
    # If using RealDictCursor this will already be a dict
    if isinstance(row, dict):
        return row
    # otherwise construct from description
    return {desc[0]: row[idx] for idx, desc in enumerate(cur.description)}


def add_user(conn, user_id: int, username: str) -> Dict[str, Any]:
    """Insert a user and return the new row."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            'INSERT INTO "Users" ("userID", username) VALUES (%s, %s) RETURNING *',
            (user_id, username),
        )
        conn.commit()
        return cur.fetchone()


def delete_user(conn, user_id: int) -> bool:
    """Delete a user by userID. Returns True if a row was deleted."""
    with conn.cursor() as cur:
        cur.execute('DELETE FROM "Users" WHERE "userID" = %s', (user_id,))
        deleted = cur.rowcount
        conn.commit()
        return deleted > 0


def get_user(conn, user_id: int) -> Optional[Dict[str, Any]]:
    """Fetch a user by userID. Returns dict or None."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute('SELECT * FROM "Users" WHERE "userID" = %s', (user_id,))
        return _row_from_cursor(cur)


def update_user(conn, user_id: int, username: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Update a user's username. Returns the updated row or None if not found."""
    # Build dynamic SET clause
    fields = []
    values = []
    if username is not None:
        fields.append('username = %s')
        values.append(username)
    if not fields:
        return get_user(conn, user_id)
    values.append(user_id)
    query = f'UPDATE "Users" SET {", ".join(fields)} WHERE "userID" = %s RETURNING *'
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(query, tuple(values))
        conn.commit()
        return _row_from_cursor(cur)


def add_workspace(conn, workspace_id: int, user_id: int, title: Optional[str] = None, description: Optional[str] = None) -> Dict[str, Any]:
    """Insert a workspace and return the new row."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            'INSERT INTO "Workspaces" ("workspacesID", "userID", title, description) VALUES (%s, %s, %s, %s) RETURNING *',
            (workspace_id, user_id, title, description),
        )
        conn.commit()
        return cur.fetchone()


def delete_workspace(conn, workspace_id: int) -> bool:
    """Delete a workspace by workspacesID. Returns True if a row was deleted."""
    with conn.cursor() as cur:
        cur.execute('DELETE FROM "Workspaces" WHERE "workspacesID" = %s', (workspace_id,))
        deleted = cur.rowcount
        conn.commit()
        return deleted > 0


def get_workspace(conn, workspace_id: int) -> Optional[Dict[str, Any]]:
    """Fetch a workspace by workspacesID. Returns dict or None."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute('SELECT * FROM "Workspaces" WHERE "workspacesID" = %s', (workspace_id,))
        return _row_from_cursor(cur)


def update_workspace(conn, workspace_id: int, title: Optional[str] = None, description: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Update workspace title/description. Returns updated row or None if not found."""
    fields = []
    values = []
    if title is not None:
        fields.append('title = %s')
        values.append(title)
    if description is not None:
        fields.append('description = %s')
        values.append(description)
    if not fields:
        return get_workspace(conn, workspace_id)
    values.append(workspace_id)
    query = f'UPDATE "Workspaces" SET {", ".join(fields)} WHERE "workspacesID" = %s RETURNING *'
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(query, tuple(values))
        conn.commit()
        return _row_from_cursor(cur)


def add_node(conn, node_id: int, title: str, workspace_id: int, description: Optional[str] = None, connected_titles: Optional[List[str]] = None, connected_ids: Optional[List[int]] = None) -> Dict[str, Any]:
    """Insert a node and return the new row.

    connected_titles is stored as text[] and connected_ids as integer[].
    """
    # Ensure arrays are provided as list or None
    ct = connected_titles if connected_titles is not None else None
    ci = connected_ids if connected_ids is not None else None
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            'INSERT INTO "Node" ("nodeID", title, description, "connectedTitles", "connectedIDs", "workspaceID") VALUES (%s, %s, %s, %s, %s, %s) RETURNING *',
            (node_id, title, description, ct, ci, workspace_id),
        )
        conn.commit()
        return cur.fetchone()


def delete_node(conn, node_id: int) -> bool:
    """Delete a node by nodeID. Returns True if a row was deleted."""
    with conn.cursor() as cur:
        cur.execute('DELETE FROM "Node" WHERE "nodeID" = %s', (node_id,))
        deleted = cur.rowcount
        conn.commit()
        return deleted > 0


def get_node(conn, node_id: int) -> Optional[Dict[str, Any]]:
    """Fetch a node by nodeID. Returns dict or None."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute('SELECT * FROM "Node" WHERE "nodeID" = %s', (node_id,))
        return _row_from_cursor(cur)


def update_node(conn, node_id: int, title: Optional[str] = None, description: Optional[str] = None, connected_titles: Optional[List[str]] = None, connected_ids: Optional[List[int]] = None) -> Optional[Dict[str, Any]]:
    """Update node fields. Returns updated row or None if not found."""
    fields = []
    values = []
    if title is not None:
        fields.append('title = %s')
        values.append(title)
    if description is not None:
        fields.append('description = %s')
        values.append(description)
    if connected_titles is not None:
        fields.append('"connectedTitles" = %s')
        values.append(connected_titles)
    if connected_ids is not None:
        fields.append('"connectedIDs" = %s')
        values.append(connected_ids)
    if not fields:
        return get_node(conn, node_id)
    values.append(node_id)
    query = f'UPDATE "Node" SET {", ".join(fields)} WHERE "nodeID" = %s RETURNING *'
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(query, tuple(values))
        conn.commit()
        return _row_from_cursor(cur)
    
def node_exists(conn, node_id: int) -> bool:
    with conn.cursor() as cur:
        cur.execute('SELECT * FROM "Node" WHERE "nodeID" = %s', (node_id,))
        return cur.fetchone() is not None

def node_table_size(conn) -> int:
    """Returns the number of rows in the Node table."""
    try:
        with conn.cursor() as cur:
            cur.execute('SELECT COUNT(*) FROM "Node"')
            count = cur.fetchone()[0]
            return count
    finally:
        conn.close()