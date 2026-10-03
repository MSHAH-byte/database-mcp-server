from mcp.server.mcpserver import MCPServer
from mcp.types import ToolAnnotations

from tools import (
    get_database_schema,
    execute_read_only_query,
    get_slow_queries,
)


server = MCPServer("Database Inspection Server")


@server.tool(
    name="get_database_schema",
    description="Inspect the SQLite database and return all tables, columns, and foreign-key relationships.",
    annotations=ToolAnnotations(
        read_only_hint=True,
        destructive_hint=False,
        idempotent_hint=True,
        open_world_hint=False,
    ),
)
def database_schema() -> dict:
    return get_database_schema()


@server.tool(
    name="execute_read_only_query",
    description="Execute a read-only SELECT SQL query against the SQLite database.",
    annotations=ToolAnnotations(
        read_only_hint=True,
        destructive_hint=False,
        idempotent_hint=True,
        open_world_hint=False,
    ),
)
def read_only_query(query: str) -> dict:
    return execute_read_only_query(query)


@server.tool(
    name="get_slow_queries",
    description="Return previously executed queries that took at least the requested amount of time.",
    annotations=ToolAnnotations(
        read_only_hint=True,
        destructive_hint=False,
        idempotent_hint=True,
        open_world_hint=False,
    ),
)
def slow_queries(
    min_duration_ms: float = 0,
    limit: int = 10,
) -> list[dict]:
    return get_slow_queries(min_duration_ms, limit)


if __name__ == "__main__":
    server.run(transport="stdio")