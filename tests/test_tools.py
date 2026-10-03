import sqlite3

import tools


def test_get_database_schema(monkeypatch):
    """Verify that the schema tool returns tables and relationships."""

    monkeypatch.setattr(
        tools,
        "get_tables",
        lambda: ["users", "orders"],
    )

    monkeypatch.setattr(
        tools,
        "get_columns",
        lambda table: (
            [
                {
                    "name": "id",
                    "type": "INTEGER",
                    "not_null": False,
                    "primary_key": True,
                }
            ]
            if table == "users"
            else [
                {
                    "name": "user_id",
                    "type": "INTEGER",
                    "not_null": True,
                    "primary_key": False,
                }
            ]
        ),
    )

    monkeypatch.setattr(
        tools,
        "get_foreign_keys",
        lambda table: (
            []
            if table == "users"
            else [
                {
                    "column": "user_id",
                    "references_table": "users",
                    "references_column": "id",
                }
            ]
        ),
    )

    result = tools.get_database_schema()

    assert result["database"] == "SQLite"
    assert "users" in result["tables"]
    assert "orders" in result["tables"]

    assert result["tables"]["users"]["columns"][0]["name"] == "id"

    assert result["tables"]["orders"]["foreign_keys"][0] == {
        "column": "user_id",
        "references_table": "users",
        "references_column": "id",
    }


def test_execute_read_only_query():
    """Verify that a valid SELECT query executes successfully."""

    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row

    connection.execute(
        "CREATE TABLE users (id INTEGER, name TEXT)"
    )

    connection.executemany(
        "INSERT INTO users (id, name) VALUES (?, ?)",
        [
            (1, "Ali"),
            (2, "Sara"),
        ],
    )

    connection.commit()

    original_get_connection = tools.get_connection
    tools.get_connection = lambda: connection

    try:
        result = tools.execute_read_only_query(
            "SELECT * FROM users"
        )
    finally:
        tools.get_connection = original_get_connection
        connection.close()

    assert result["success"] is True
    assert result["row_count"] == 2
    assert result["rows"] == [
        {"id": 1, "name": "Ali"},
        {"id": 2, "name": "Sara"},
    ]
    assert "duration_ms" in result


def test_execute_read_only_query_rejects_non_select():
    """Verify that non-SELECT SQL statements are rejected."""

    result = tools.execute_read_only_query(
        "DELETE FROM users"
    )

    assert result["success"] is False
    assert result["error"] == "Only SELECT queries are allowed."


def test_get_slow_queries():
    """Verify slow-query filtering and ordering."""

    original_logs = tools.QUERY_LOGS

    tools.QUERY_LOGS = [
        {
            "query": "SELECT * FROM users",
            "duration_ms": 15.0,
            "row_count": 3,
        },
        {
            "query": "SELECT * FROM orders",
            "duration_ms": 50.0,
            "row_count": 4,
        },
        {
            "query": "SELECT name FROM users",
            "duration_ms": 5.0,
            "row_count": 3,
        },
    ]

    try:
        result = tools.get_slow_queries(
            min_duration_ms=10,
            limit=10,
        )
    finally:
        tools.QUERY_LOGS = original_logs

    assert len(result) == 2

    assert result[0]["query"] == "SELECT * FROM orders"
    assert result[0]["duration_ms"] == 50.0

    assert result[1]["query"] == "SELECT * FROM users"
    assert result[1]["duration_ms"] == 15.0


def test_get_slow_queries_respects_limit():
    """Verify that get_slow_queries respects the result limit."""

    original_logs = tools.QUERY_LOGS

    tools.QUERY_LOGS = [
        {
            "query": "SELECT 1",
            "duration_ms": 30.0,
            "row_count": 1,
        },
        {
            "query": "SELECT 2",
            "duration_ms": 20.0,
            "row_count": 1,
        },
        {
            "query": "SELECT 3",
            "duration_ms": 10.0,
            "row_count": 1,
        },
    ]

    try:
        result = tools.get_slow_queries(
            min_duration_ms=0,
            limit=2,
        )
    finally:
        tools.QUERY_LOGS = original_logs

    assert len(result) == 2
    assert result[0]["duration_ms"] == 30.0
    assert result[1]["duration_ms"] == 20.0