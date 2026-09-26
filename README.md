# Database MCP Server

A Python-based **Model Context Protocol (MCP) server** that exposes a SQLite database to MCP clients through structured tools for database inspection, read-only SQL execution, and query performance monitoring.

This project was built to understand how **MCP servers expose capabilities to AI applications** through the MCP protocol.

## Features

* Inspect database schema dynamically
* List tables, columns, and foreign-key relationships
* Execute **read-only `SELECT` queries**
* Return structured query results
* Record query execution time
* Inspect recently executed queries
* MCP communication over **stdio**
* Built with the official Python MCP SDK

## Architecture

```text
                    MCP Client
              (MCP Inspector / Claude)
                       │
                       │ MCP / stdio
                       ▼
                ┌─────────────┐
                │  server.py  │
                │ MCP Server  │
                └──────┬──────┘
                       │
                  MCP Tools
                       │
                       ▼
                ┌─────────────┐
                │  tools.py   │
                │             │
                │ • Schema    │
                │ • SQL       │
                │ • Monitoring│
                └──────┬──────┘
                       │
                 Database Logic
                       │
                       ▼
                ┌─────────────┐
                │    db.py    │
                └──────┬──────┘
                       │
                       ▼
                ┌─────────────┐
                │  SQLite DB  │
                │   app.db    │
                └─────────────┘
```

## MCP Tools

### `get_database_schema`

Returns the database structure, including:

* Tables
* Columns
* Data types
* Primary keys
* Foreign keys

Example result:

```json
{
  "database": "SQLite",
  "tables": {
    "orders": {
      "columns": [],
      "foreign_keys": []
    },
    "users": {
      "columns": [],
      "foreign_keys": []
    }
  }
}
```

### `execute_read_only_query`

Executes a SQL query against the database.

Only `SELECT` queries are permitted.

Example:

```sql
SELECT users.name, orders.product, orders.amount
FROM users
JOIN orders ON users.id = orders.user_id;
```

The tool returns:

* Query success/failure
* Rows
* Row count
* Execution time

Write operations such as `INSERT`, `UPDATE`, and `DELETE` are rejected.

### `get_slow_queries`

Returns queries recorded during the current MCP server session, including:

* SQL query
* Execution duration
* Number of returned rows

Queries can be filtered by minimum execution time and limited by result count.

> Query history is stored in memory and is reset when the MCP server restarts. This is intentional for this learning project.

## Database

The project uses a small SQLite database containing two related tables:

```text
users
-----
id
name
email

orders
------
id
user_id
product
amount
```

Relationship:

```text
users.id
   │
   │
   └──────< orders.user_id
```

Sample data is included automatically when the database is initialized.

## Project Structure

```text
Database_MCP_Server/
│
├── database/
│   └── app.db
│
├── src/
│   ├── db.py
│   ├── tools.py
│   └── server.py
│
├── .gitignore
├── LICENSE
├── requirements.txt
└── README.md
```

### `src/db.py`

Handles SQLite database operations:

* Database initialization
* Connections
* Table discovery
* Column inspection
* Foreign-key inspection
* SQL execution

### `src/tools.py`

Contains the actual capabilities exposed through MCP:

* Database schema inspection
* Read-only SQL execution
* Query performance logging

### `src/server.py`

Creates the MCP server and exposes the Python functions as MCP tools.

The server communicates using **stdio transport**.

## Requirements

* Python 3.12+
* Node.js / npm
* MCP Python SDK 2.x

## Installation

Clone the repository:

```bash
git clone https://github.com/MSHAH-byte/database-mcp-server.git
```

Enter the project directory:

```bash
cd database-mcp-server
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Database Initialization

The sample database can be initialized by running:

```powershell
python .\src\db.py
```

This creates:

```text
database/app.db
```

with the sample `users` and `orders` tables.

## Running the MCP Server

The server uses stdio transport and is intended to be launched by an MCP client.

Run:

```powershell
python .\src\server.py
```

The terminal will wait for MCP communication rather than displaying a normal application interface.

## Testing with MCP Inspector

MCP Inspector can be used to connect to and interact with the server.

Run:

```powershell
npx @modelcontextprotocol/inspector python .\src\server.py
```

Inspector should connect to the server and discover the available tools.

You can then test:

```text
get_database_schema
execute_read_only_query
get_slow_queries
```

### Example Query

```sql
SELECT * FROM users;
```

Expected sample users:

```text
Ali
Sara
Ahmed
```

### Example JOIN

```sql
SELECT users.name, orders.product, orders.amount
FROM users
JOIN orders ON users.id = orders.user_id;
```

### Read-Only Protection

Attempting:

```sql
DELETE FROM users;
```

returns an error because the server only permits `SELECT` queries.

## Security Considerations

This project intentionally exposes a limited database capability.

The SQL tool:

* Allows only `SELECT` statements
* Rejects multiple SQL statements
* Does not expose database write operations
* Does not expose arbitrary filesystem access
* Does not contain API keys or credentials

This is a learning implementation rather than a production database security layer.

For a production system, SQL validation, authentication, authorization, database permissions, auditing, query limits, and resource controls would require substantially more robust implementation.

## What This Project Demonstrates

The main purpose of this project is understanding the MCP architecture.

Without MCP:

```text
AI Application
      │
      └── custom integration
              │
              └── database
```

With MCP:

```text
AI Application
      │
      ▼
   MCP Client
      │
      │ MCP
      ▼
  MCP Server
      │
      ▼
    Tools
      │
      ▼
  Database
```

The MCP client can discover the capabilities exposed by the server through the protocol instead of requiring the database integration to be hard-coded into every AI application.

## Key MCP Concepts Learned

* MCP client/server architecture
* MCP server initialization
* stdio transport
* Tool registration
* Tool discovery
* Tool descriptions and schemas
* Tool invocation
* Structured tool results
* Separating MCP tools from application logic
* Restricting tool permissions
* Connecting AI applications to external capabilities

## Limitations

This project intentionally keeps the scope small.

* SQLite only
* Query history is stored in memory
* No authentication
* No persistent monitoring system
* No production-grade SQL parser
* No database write operations
* No remote transport
* No multi-server architecture

These limitations keep the project focused on learning the core MCP concepts.

## Next Step

The next MCP project will extend these concepts into a **multi-server DevOps / Incident Response system**, where an AI agent interacts with multiple independent MCP servers for system logs and GitHub operations, with human approval before side-effecting actions.

## License

This project is licensed under the MIT License. See [LICENSE](./LICENSE).
