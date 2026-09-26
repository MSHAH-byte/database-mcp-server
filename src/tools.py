import time
from typing import Any

from db import (
    get_tables,
    get_columns,
    get_foreign_keys,
    get_connection,
)


# Stores query performance information while the MCP server is running.
QUERY_LOGS: list[dict[str, Any]] = []


def get_database_schema() -> dict[str, Any]:
    """
    Return the complete schema of the SQLite database.

    Includes:
    - tables
    - columns
    - foreign-key relationships
    """

    schema = {}

    for table in get_tables():
        schema[table] = {
            "columns": get_columns(table),
            "foreign_keys": get_foreign_keys(table),
        }

    return {
        "database": "SQLite",
        "tables": schema,
    }


def execute_read_only_query(query: str) -> dict[str, Any]:
    """
    Execute a SELECT-only SQL query.

    Only SELECT statements are allowed.
    """

    query = query.strip()

    if not query:
        return {
            "success": False,
            "error": "Query cannot be empty.",
        }

    # Strictly allow SELECT statements only.
    if not query.upper().startswith("SELECT "):
        return {
            "success": False,
            "error": "Only SELECT queries are allowed.",
        }

    # Prevent multiple SQL statements.
    if ";" in query[:-1]:
        return {
            "success": False,
            "error": "Multiple SQL statements are not allowed.",
        }

    start_time = time.perf_counter()

    connection = get_connection()

    try:
        rows = connection.execute(query).fetchall()

        duration_ms = (time.perf_counter() - start_time) * 1000

        QUERY_LOGS.append(
            {
                "query": query,
                "duration_ms": round(duration_ms, 2),
                "row_count": len(rows),
            }
        )

        return {
            "success": True,
            "rows": [dict(row) for row in rows],
            "row_count": len(rows),
            "duration_ms": round(duration_ms, 2),
        }

    except Exception as error:
        return {
            "success": False,
            "error": str(error),
        }

    finally:
        connection.close()


def get_slow_queries(
    min_duration_ms: float = 0,
    limit: int = 10,
) -> list[dict[str, Any]]:
    """
    Return recorded queries that took at least min_duration_ms.

    Query history exists only for the lifetime of the MCP server process.
    """

    matching_queries = [
        query
        for query in QUERY_LOGS
        if query["duration_ms"] >= min_duration_ms
    ]

    matching_queries.sort(
        key=lambda query: query["duration_ms"],
        reverse=True,
    )

    return matching_queries[:limit]