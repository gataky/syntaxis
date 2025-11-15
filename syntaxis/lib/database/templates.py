"""Template storage operations for SQLite database."""

import logging
import sqlite3

logger = logging.getLogger(__name__)


def save_template(conn: sqlite3.Connection, template: str) -> dict:
    """Save a template to the database.

    Args:
        conn: SQLite database connection
        template: Template string to save

    Returns:
        Dict with id, template, and created_at

    Raises:
        ValueError: If template already exists
    """
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO templates (template) VALUES (?)", (template,))
        conn.commit()
        template_id = cursor.lastrowid

        # Fetch the created record
        cursor.execute(
            "SELECT id, template, created_at FROM templates WHERE id = ?",
            (template_id,),
        )
        row = cursor.fetchone()

        return {
            "id": row["id"],
            "template": row["template"],
            "created_at": row["created_at"],
        }

    except sqlite3.IntegrityError as e:
        if "UNIQUE constraint failed" in str(e):
            raise ValueError("Template already exists")
        raise


def list_templates(conn: sqlite3.Connection) -> list[dict]:
    """List all templates ordered by created_at descending.

    Args:
        conn: SQLite database connection

    Returns:
        List of template dicts
    """
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, template, created_at FROM templates ORDER BY created_at DESC"
    )
    rows = cursor.fetchall()

    return [
        {"id": row["id"], "template": row["template"], "created_at": row["created_at"]}
        for row in rows
    ]


def get_template(conn: sqlite3.Connection, template_id: int) -> dict | None:
    """Get a template by ID.

    Args:
        conn: SQLite database connection
        template_id: Template ID

    Returns:
        Template dict or None if not found
    """
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, template, created_at FROM templates WHERE id = ?", (template_id,)
    )
    row = cursor.fetchone()

    if not row:
        return None

    return {
        "id": row["id"],
        "template": row["template"],
        "created_at": row["created_at"],
    }


def delete_template(conn: sqlite3.Connection, template_id: int) -> bool:
    """Delete a template by ID.

    Args:
        conn: SQLite database connection
        template_id: Template ID

    Returns:
        True if deleted, False if not found
    """
    cursor = conn.cursor()
    cursor.execute("DELETE FROM templates WHERE id = ?", (template_id,))
    conn.commit()

    return cursor.rowcount > 0
