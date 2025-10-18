import json
import os
import sqlite3
from typing import Any

try:
    import psycopg2
    from psycopg2 import pool
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False


class Repo:
    """Database repository with PostgreSQL (production) and SQLite (local dev) support."""

    _connection_pool = None

    def __init__(self, db_url: str = None):
        """
        Initialize repository with PostgreSQL or SQLite.

        Args:
            db_url: Database connection URL. If None, uses DATABASE_URL env var.
                   PostgreSQL URLs start with postgres:// or postgresql://
                   File paths use SQLite for local development.
        """
        self.db_url = db_url or os.environ.get('DATABASE_URL')
        self.use_postgres = False

        # Determine database type
        if self.db_url and self.db_url.startswith(('postgres://', 'postgresql://')):
            if not PSYCOPG2_AVAILABLE:
                raise ImportError("psycopg2 is required for PostgreSQL connections")
            self.use_postgres = True
            self._init_pool()
        else:
            # Fallback to SQLite for local development
            self.db_url = self.db_url or 'pipeline_results.db'
            print(f"INFO: Using SQLite for local development: {self.db_url}")

        self._init_db()

    def _init_pool(self) -> None:
        """Initialize PostgreSQL connection pool (shared across instances)."""
        if not self.use_postgres:
            return

        if Repo._connection_pool is None and self.db_url:
            try:
                Repo._connection_pool = pool.SimpleConnectionPool(
                    minconn=1,
                    maxconn=10,
                    dsn=self.db_url
                )
            except Exception as e:
                print(f"Warning: Could not create connection pool: {e}")
                print("Falling back to direct connections")

    def _get_connection(self):
        """Get a database connection (PostgreSQL from pool, SQLite direct)."""
        if self.use_postgres:
            if Repo._connection_pool:
                return Repo._connection_pool.getconn()
            return psycopg2.connect(self.db_url)
        else:
            return sqlite3.connect(self.db_url)

    def _return_connection(self, conn):
        """Return connection to pool (PostgreSQL) or close it (SQLite)."""
        if self.use_postgres and Repo._connection_pool:
            Repo._connection_pool.putconn(conn)
        else:
            conn.close()

    def _init_db(self) -> None:
        """Create tables if they don't exist."""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Use SERIAL for PostgreSQL, INTEGER PRIMARY KEY AUTOINCREMENT for SQLite
        id_type = "SERIAL PRIMARY KEY" if self.use_postgres else "INTEGER PRIMARY KEY AUTOINCREMENT"

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS enhanced_pipeline_runs (
                run_timestamp TEXT NOT NULL,
                topic TEXT NOT NULL,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                total_steps INTEGER,
                differentiation_achieved BOOLEAN,
                final_success BOOLEAN,
                PRIMARY KEY (run_timestamp, topic)
            )
            """
        )
        cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS enhanced_step_responses (
                id {id_type},
                run_timestamp TEXT NOT NULL,
                topic TEXT NOT NULL,
                step_number INTEGER NOT NULL,
                step_name TEXT NOT NULL,
                model_used TEXT NOT NULL,
                success BOOLEAN NOT NULL,
                response_length INTEGER NOT NULL,
                full_response TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS step_rewards (
                id {id_type},
                run_timestamp TEXT NOT NULL,
                step_number INTEGER NOT NULL,
                pass_rate REAL NOT NULL,
                num_tests INTEGER NOT NULL,
                detail_json TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()
        self._return_connection(conn)

    def save_step(
        self,
        run_timestamp: str,
        topic: str,
        step_number: int,
        step_name: str,
        model_used: str,
        success: bool,
        response: str,
        timestamp: str,
    ) -> None:
        conn = self._get_connection()
        cursor = conn.cursor()

        # Use %s for PostgreSQL, ? for SQLite
        placeholder = "%s" if self.use_postgres else "?"

        cursor.execute(
            f"""
            INSERT INTO enhanced_step_responses
            (run_timestamp, topic, step_number, step_name, model_used, success,
             response_length, full_response, timestamp)
            VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
            """,
            (
                run_timestamp,
                topic,
                step_number,
                step_name,
                model_used,
                success if self.use_postgres else int(bool(success)),  # PostgreSQL handles booleans natively
                len(response or ""),
                response or "",
                timestamp,
            ),
        )
        conn.commit()
        self._return_connection(conn)

    def save_rewards(
        self,
        run_timestamp: str,
        step_number: int,
        pass_rate: float,
        details: list[dict[str, Any]],
    ) -> None:
        conn = self._get_connection()
        cursor = conn.cursor()
        placeholder = "%s" if self.use_postgres else "?"

        cursor.execute(
            f"""
            INSERT INTO step_rewards (run_timestamp, step_number, pass_rate, num_tests, detail_json)
            VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
            """,
            (
                run_timestamp,
                step_number,
                pass_rate,
                len(details),
                json.dumps(details),
            ),
        )
        conn.commit()
        self._return_connection(conn)

    def mark_run_start(self, run_timestamp: str, topic: str) -> None:
        conn = self._get_connection()
        cursor = conn.cursor()
        placeholder = "%s" if self.use_postgres else "?"

        if self.use_postgres:
            # PostgreSQL uses ON CONFLICT
            cursor.execute(
                f"""
                INSERT INTO enhanced_pipeline_runs (run_timestamp, topic)
                VALUES ({placeholder}, {placeholder})
                ON CONFLICT (run_timestamp) DO NOTHING
                """,
                (run_timestamp, topic),
            )
        else:
            # SQLite uses INSERT OR IGNORE
            cursor.execute(
                f"""
                INSERT OR IGNORE INTO enhanced_pipeline_runs (run_timestamp, topic)
                VALUES ({placeholder}, {placeholder})
                """,
                (run_timestamp, topic),
            )

        conn.commit()
        self._return_connection(conn)

    def mark_run_end(
        self,
        run_timestamp: str,
        total_steps: int,
        differentiation_achieved: bool,
        final_success: bool,
    ) -> None:
        conn = self._get_connection()
        cursor = conn.cursor()
        placeholder = "%s" if self.use_postgres else "?"

        cursor.execute(
            f"""
            UPDATE enhanced_pipeline_runs
            SET
                completed_at = CURRENT_TIMESTAMP,
                total_steps = {placeholder},
                differentiation_achieved = {placeholder},
                final_success = {placeholder}
            WHERE run_timestamp = {placeholder}
            """,
            (
                total_steps,
                differentiation_achieved if self.use_postgres else int(bool(differentiation_achieved)),
                final_success if self.use_postgres else int(bool(final_success)),
                run_timestamp,
            ),
        )
        conn.commit()
        self._return_connection(conn)
