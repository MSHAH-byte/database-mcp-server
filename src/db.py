import sqlite3
from pathlib import Path


DATABASE_DIR = Path(__file__).resolve().parent.parent / "database"
DATABASE_PATH = DATABASE_DIR / "app.db"


def get_connection() -> sqlite3.Connection:
    """Create a connection to the SQLite database."""
    DATABASE_DIR.mkdir(exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    # Enforce foreign-key relationships.
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def initialize_database() -> None:
    """Create the demo database and sample data."""
    connection = get_connection()

    try:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE
            );

            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                product TEXT NOT NULL,
                amount REAL NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );

            INSERT OR IGNORE INTO users (id, name, email)
            VALUES
                (1, 'Ali', 'ali@example.com'),
                (2, 'Sara', 'sara@example.com'),
                (3, 'Ahmed', 'ahmed@example.com');

            INSERT OR IGNORE INTO orders (id, user_id, product, amount)
            VALUES
                (1, 1, 'Laptop', 1200.00),
                (2, 1, 'Mouse', 25.00),
                (3, 2, 'Keyboard', 75.00),
                (4, 3, 'Monitor', 300.00);
            """
        )

        connection.commit()

    finally:
        connection.close()


def get_tables() -> list[str]:
    """Return all user-created tables."""
    connection = get_connection()

    try:
        rows = connection.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            AND name NOT LIKE 'sqlite_%'
            ORDER BY name
            """
        ).fetchall()

        return [row["name"] for row in rows]

    finally:
        connection.close()


def get_columns(table_name: str) -> list[dict]:
    """Return column information for a table."""
    connection = get_connection()

    try:
        # SQLite does not allow a table name to be passed as a
        # parameter to PRAGMA, so escape it as a SQLite identifier.
        safe_table_name = table_name.replace('"', '""')

        rows = connection.execute(
            f'PRAGMA table_info("{safe_table_name}")'
        ).fetchall()

        return [
            {
                "name": row["name"],
                "type": row["type"],
                "not_null": bool(row["notnull"]),
                "primary_key": bool(row["pk"]),
            }
            for row in rows
        ]

    finally:
        connection.close()


def get_foreign_keys(table_name: str) -> list[dict]:
    """Return foreign-key relationships for a table."""
    connection = get_connection()

    try:
        safe_table_name = table_name.replace('"', '""')

        rows = connection.execute(
            f'PRAGMA foreign_key_list("{safe_table_name}")'
        ).fetchall()

        return [
            {
                "column": row["from"],
                "references_table": row["table"],
                "references_column": row["to"],
            }
            for row in rows
        ]

    finally:
        connection.close()


if __name__ == "__main__":
    initialize_database()

    print(f"Database created at: {DATABASE_PATH}")
    print("Tables:", get_tables())