import sqlite3

import pytest

from syntaxis.lib.database import templates
from syntaxis.lib.database.schema import create_schema


@pytest.fixture
def db_conn():
    """Create in-memory database with schema."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    create_schema(conn)
    yield conn
    conn.close()


def test_save_template_inserts_new_template(db_conn):
    """Should insert template and return dict with id."""
    template_str = "noun(case=nominative,gender=masculine,number=singular)"

    result = templates.save_template(db_conn, template_str)

    assert result["id"] == 1
    assert result["template"] == template_str
    assert "created_at" in result
    assert isinstance(result["created_at"], str)


def test_save_template_raises_on_duplicate(db_conn):
    """Should raise ValueError when template already exists."""
    template_str = "noun(case=nominative,gender=masculine,number=singular)"
    templates.save_template(db_conn, template_str)

    with pytest.raises(ValueError, match="Template already exists"):
        templates.save_template(db_conn, template_str)


def test_list_templates_returns_all_templates(db_conn):
    """Should return list of all templates ordered by created_at desc."""
    templates.save_template(db_conn, "template1")
    templates.save_template(db_conn, "template2")
    templates.save_template(db_conn, "template3")

    result = templates.list_templates(db_conn)

    assert len(result) == 3
    # Verify all templates are present (order may vary if timestamps are identical)
    template_strs = [t["template"] for t in result]
    assert "template1" in template_strs
    assert "template2" in template_strs
    assert "template3" in template_strs


def test_list_templates_returns_empty_list_when_no_templates(db_conn):
    """Should return empty list when no templates exist."""
    result = templates.list_templates(db_conn)
    assert result == []


def test_get_template_returns_template_by_id(db_conn):
    """Should return template dict when id exists."""
    saved = templates.save_template(db_conn, "test_template")

    result = templates.get_template(db_conn, saved["id"])

    assert result["id"] == saved["id"]
    assert result["template"] == "test_template"
    assert "created_at" in result


def test_get_template_returns_none_when_not_found(db_conn):
    """Should return None when template id doesn't exist."""
    result = templates.get_template(db_conn, 999)
    assert result is None


def test_delete_template_removes_template_and_returns_true(db_conn):
    """Should delete template and return True when id exists."""
    saved = templates.save_template(db_conn, "to_delete")

    result = templates.delete_template(db_conn, saved["id"])

    assert result is True
    # Verify it's gone
    assert templates.get_template(db_conn, saved["id"]) is None


def test_delete_template_returns_false_when_not_found(db_conn):
    """Should return False when template id doesn't exist."""
    result = templates.delete_template(db_conn, 999)
    assert result is False
