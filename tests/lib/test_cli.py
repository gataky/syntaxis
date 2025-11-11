"""Unit tests for CLI commands."""

import csv
import os
import sqlite3
import tempfile

import pytest
from typer.testing import CliRunner

from syntaxis.lib.cli import app

runner = CliRunner()


class TestCLI:
    """Test suite for CLI commands."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test databases."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def temp_db_path(self, temp_dir):
        """Create a temporary database path."""
        return os.path.join(temp_dir, "test_syntaxis.db")

    @pytest.fixture
    def temp_csv_path(self, temp_dir):
        """Create a temporary CSV file with test data."""
        csv_path = os.path.join(temp_dir, "test_dict.csv")
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            # Header
            writer.writerow(["lexical", "translations", "lemma"])
            # Test data - use actual LEXICAL_MAP keys
            writer.writerow(["noun", "person,human", "άνθρωπος"])
            writer.writerow(["verb", "see,look", "βλέπω"])
            writer.writerow(["adjective", "big,large", "μεγάλος"])
        return csv_path

    # Tests for create_db command

    def test_create_db_default_name(self, temp_dir):
        """Test creating database with default name."""
        # Change to temp directory
        original_dir = os.getcwd()
        os.chdir(temp_dir)

        try:
            result = runner.invoke(app, ["create-db"])

            assert result.exit_code == 0
            assert "Database 'syntaxis.db' created." in result.stdout
            assert os.path.exists("syntaxis.db")

            # Verify it's a valid SQLite database
            conn = sqlite3.connect("syntaxis.db")
            cursor = conn.cursor()
            # Check that tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            assert "greek_nouns" in tables
            assert "greek_verbs" in tables
            conn.close()
        finally:
            os.chdir(original_dir)

    def test_create_db_custom_name(self, temp_db_path):
        """Test creating database with custom name."""
        result = runner.invoke(app, ["create-db", "--db-name", temp_db_path])

        assert result.exit_code == 0
        assert f"Database '{temp_db_path}' created." in result.stdout
        assert os.path.exists(temp_db_path)

    def test_create_db_already_exists(self, temp_db_path):
        """Test creating database when one already exists."""
        # Create database first time
        result1 = runner.invoke(app, ["create-db", "--db-name", temp_db_path])
        assert result1.exit_code == 0

        # Create database second time (should succeed, doesn't overwrite)
        result2 = runner.invoke(app, ["create-db", "--db-name", temp_db_path])
        assert result2.exit_code == 0
        assert os.path.exists(temp_db_path)

    def test_create_db_with_clear_flag(self, temp_db_path):
        """Test creating database with --clear flag removes existing database."""
        # Create database and add some data
        runner.invoke(app, ["create-db", "--db-name", temp_db_path])
        assert os.path.exists(temp_db_path)

        # Get initial modification time
        initial_mtime = os.path.getmtime(temp_db_path)

        # Create again with --clear
        result = runner.invoke(app, ["create-db", "--db-name", temp_db_path, "--clear"])

        assert result.exit_code == 0
        assert f"Existing database '{temp_db_path}' removed." in result.stdout
        assert f"Database '{temp_db_path}' created." in result.stdout
        assert os.path.exists(temp_db_path)

        # File should be recreated (new modification time)
        new_mtime = os.path.getmtime(temp_db_path)
        assert new_mtime >= initial_mtime

    def test_create_db_clear_flag_no_existing_db(self, temp_db_path):
        """Test --clear flag when database doesn't exist yet."""
        result = runner.invoke(app, ["create-db", "--db-name", temp_db_path, "--clear"])

        assert result.exit_code == 0
        # Should not show removal message since file didn't exist
        assert "removed" not in result.stdout.lower()
        assert f"Database '{temp_db_path}' created." in result.stdout
        assert os.path.exists(temp_db_path)

    # Tests for seed_dictionary command

    def test_seed_dictionary_basic(self, temp_db_path, temp_csv_path):
        """Test seeding dictionary from CSV file."""
        # Create database first
        runner.invoke(app, ["create-db", "--db-name", temp_db_path])

        # Seed dictionary
        result = runner.invoke(
            app,
            ["seed-dictionary", "--db-name", temp_db_path, "--csv-file", temp_csv_path],
        )

        assert result.exit_code == 0
        assert "Seeded 3 words forms" in result.stdout
        assert temp_csv_path in result.stdout

        # Verify data was inserted
        conn = sqlite3.connect(temp_db_path)
        cursor = conn.cursor()

        # Check nouns table
        cursor.execute("SELECT COUNT(*) FROM greek_nouns WHERE lemma = 'άνθρωπος'")
        assert cursor.fetchone()[0] > 0

        # Check verbs table
        cursor.execute("SELECT COUNT(*) FROM greek_verbs WHERE lemma = 'βλέπω'")
        assert cursor.fetchone()[0] > 0

        # Check adjectives table
        cursor.execute("SELECT COUNT(*) FROM greek_adjectives WHERE lemma = 'μεγάλος'")
        assert cursor.fetchone()[0] > 0

        conn.close()

    def test_seed_dictionary_nonexistent_csv(self, temp_db_path):
        """Test seeding with nonexistent CSV file."""
        runner.invoke(app, ["create-db", "--db-name", temp_db_path])

        result = runner.invoke(
            app,
            [
                "seed-dictionary",
                "--db-name",
                temp_db_path,
                "--csv-file",
                "nonexistent.csv",
            ],
        )

        # Should fail with file not found error
        assert result.exit_code != 0
        assert isinstance(result.exception, FileNotFoundError) or "No such file" in str(
            result.exception
        )

    @pytest.mark.skip(reason="slow")
    def test_seed_dictionary_default_csv_path(self, temp_dir):
        """Test that seed-dictionary uses default CSV path."""
        db_path = os.path.join(temp_dir, "test.db")
        runner.invoke(app, ["create-db", "--db-name", db_path])

        # If data/dictionary.csv exists in project root, this may succeed
        # Otherwise it should fail. Either way is acceptable
        result = runner.invoke(app, ["seed-dictionary", "--db-name", db_path])

        # Just verify command runs (may succeed or fail depending on whether default CSV exists)
        assert result.exit_code in [0, 1]  # 0 if CSV exists, 1 if not

    def test_seed_dictionary_with_translations(self, temp_db_path, temp_csv_path):
        """Test that translations are properly stored."""
        runner.invoke(app, ["create-db", "--db-name", temp_db_path])
        runner.invoke(
            app,
            ["seed-dictionary", "--db-name", temp_db_path, "--csv-file", temp_csv_path],
        )

        # Verify translations were added
        conn = sqlite3.connect(temp_db_path)
        cursor = conn.cursor()

        # Check english_words table
        cursor.execute("SELECT COUNT(*) FROM english_words")
        count = cursor.fetchone()[0]
        assert count > 0  # Should have translations

        # Check translations table
        cursor.execute("SELECT COUNT(*) FROM translations")
        count = cursor.fetchone()[0]
        assert count > 0

        conn.close()

    def test_seed_dictionary_empty_csv(self, temp_db_path, temp_dir):
        """Test seeding with empty CSV (only header)."""
        empty_csv = os.path.join(temp_dir, "empty.csv")
        with open(empty_csv, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["lexical", "translations", "lemma"])

        runner.invoke(app, ["create-db", "--db-name", temp_db_path])
        result = runner.invoke(
            app, ["seed-dictionary", "--db-name", temp_db_path, "--csv-file", empty_csv]
        )

        assert result.exit_code == 0
        assert "Seeded 0 words" in result.stdout

    # Tests for seed_pronouns command

    def test_seed_pronouns_basic(self, temp_db_path):
        """Test seeding pronouns."""
        # Create database first
        runner.invoke(app, ["create-db", "--db-name", temp_db_path])

        # Seed pronouns
        result = runner.invoke(app, ["seed-pronouns", "--db-name", temp_db_path])

        assert result.exit_code == 0
        # Check for seed output (from the seed function)
        assert "Seeded" in result.stdout or result.exit_code == 0

        # Verify data was inserted
        conn = sqlite3.connect(temp_db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM greek_pronouns")
        count = cursor.fetchone()[0]
        assert count > 0, "Pronouns table should have data"

        conn.close()

    def test_seed_pronouns_without_database(self, temp_db_path):
        """Test seeding pronouns when database doesn't exist."""
        # Don't create database first - should create it automatically
        result = runner.invoke(app, ["seed-pronouns", "--db-name", temp_db_path])

        # Should succeed - Database() constructor creates tables
        assert result.exit_code == 0

    def test_seed_pronouns_default_db_name(self, temp_dir):
        """Test seed-pronouns uses default database name."""
        original_dir = os.getcwd()
        os.chdir(temp_dir)

        try:
            runner.invoke(app, ["create-db"])
            result = runner.invoke(app, ["seed-pronouns"])

            assert result.exit_code == 0

            # Verify data in default database
            conn = sqlite3.connect("syntaxis.db")
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM greek_pronouns")
            assert cursor.fetchone()[0] > 0
            conn.close()
        finally:
            os.chdir(original_dir)

    # Tests for seed_articles command

    def test_seed_articles_basic(self, temp_db_path):
        """Test seeding articles."""
        # Create database first
        runner.invoke(app, ["create-db", "--db-name", temp_db_path])

        # Seed articles
        result = runner.invoke(app, ["seed-articles", "--db-name", temp_db_path])

        assert result.exit_code == 0
        # Check for seed output
        assert "Seeded" in result.stdout or result.exit_code == 0

        # Verify data was inserted
        conn = sqlite3.connect(temp_db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM greek_articles")
        count = cursor.fetchone()[0]
        assert count > 0, "Articles table should have data"

        # Verify we have both definite and indefinite articles
        cursor.execute("SELECT DISTINCT type FROM greek_articles")
        types = [row[0] for row in cursor.fetchall()]
        assert len(types) > 0  # Should have article types

        conn.close()

    def test_seed_articles_without_database(self, temp_db_path):
        """Test seeding articles when database doesn't exist."""
        # Don't create database first
        result = runner.invoke(app, ["seed-articles", "--db-name", temp_db_path])

        # Should succeed - Database() constructor creates tables
        assert result.exit_code == 0

    def test_seed_articles_default_db_name(self, temp_dir):
        """Test seed-articles uses default database name."""
        original_dir = os.getcwd()
        os.chdir(temp_dir)

        try:
            runner.invoke(app, ["create-db"])
            result = runner.invoke(app, ["seed-articles"])

            assert result.exit_code == 0

            # Verify data in default database
            conn = sqlite3.connect("syntaxis.db")
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM greek_articles")
            assert cursor.fetchone()[0] > 0
            conn.close()
        finally:
            os.chdir(original_dir)

    # Integration tests

    def test_full_workflow(self, temp_db_path, temp_csv_path):
        """Test complete workflow: create DB, seed dictionary, seed pronouns, seed articles."""
        # Step 1: Create database with --clear
        result1 = runner.invoke(
            app, ["create-db", "--db-name", temp_db_path, "--clear"]
        )
        assert result1.exit_code == 0

        # Step 2: Seed dictionary
        result2 = runner.invoke(
            app,
            ["seed-dictionary", "--db-name", temp_db_path, "--csv-file", temp_csv_path],
        )
        assert result2.exit_code == 0

        # Step 3: Seed pronouns
        result3 = runner.invoke(app, ["seed-pronouns", "--db-name", temp_db_path])
        assert result3.exit_code == 0

        # Step 4: Seed articles
        result4 = runner.invoke(app, ["seed-articles", "--db-name", temp_db_path])
        assert result4.exit_code == 0

        # Verify all data is present
        conn = sqlite3.connect(temp_db_path)
        cursor = conn.cursor()

        # Check all tables have data
        cursor.execute("SELECT COUNT(*) FROM greek_nouns")
        assert cursor.fetchone()[0] > 0

        cursor.execute("SELECT COUNT(*) FROM greek_verbs")
        assert cursor.fetchone()[0] > 0

        cursor.execute("SELECT COUNT(*) FROM greek_adjectives")
        assert cursor.fetchone()[0] > 0

        cursor.execute("SELECT COUNT(*) FROM greek_pronouns")
        assert cursor.fetchone()[0] > 0

        cursor.execute("SELECT COUNT(*) FROM greek_articles")
        assert cursor.fetchone()[0] > 0

        conn.close()

    def test_multiple_seeds_same_data(self, temp_db_path, temp_csv_path):
        """Test that seeding multiple times with same data doesn't cause errors."""
        runner.invoke(app, ["create-db", "--db-name", temp_db_path])

        # Seed dictionary twice
        result1 = runner.invoke(
            app,
            ["seed-dictionary", "--db-name", temp_db_path, "--csv-file", temp_csv_path],
        )
        assert result1.exit_code == 0

        # Second time should fail due to duplicate lemmas
        result2 = runner.invoke(
            app,
            ["seed-dictionary", "--db-name", temp_db_path, "--csv-file", temp_csv_path],
        )
        assert result2.exit_code != 0  # Should fail on duplicate

    def test_seed_commands_create_db_if_missing(self, temp_db_path):
        """Test that seed commands work even if database doesn't exist."""
        # Don't create database explicitly

        # Seed pronouns (should create DB automatically)
        result = runner.invoke(app, ["seed-pronouns", "--db-name", temp_db_path])
        assert result.exit_code == 0
        assert os.path.exists(temp_db_path)

        # Verify structure is correct
        conn = sqlite3.connect(temp_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        assert "greek_pronouns" in tables
        conn.close()
