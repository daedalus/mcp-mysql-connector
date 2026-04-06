# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

### Added
- Initial release with MCP server exposing MySQL tools:
  - Connection management (connect, disconnect, pool)
  - Query execution (SELECT, INSERT, UPDATE, DELETE)
  - Database management (create, drop, list databases)
  - Table management (create, drop, describe, list tables)
  - Index management (create, drop indexes)
  - User management (create, drop, grant, revoke users)
  - Transaction support (commit, rollback)
  - Schema introspection (describe, show columns, show indexes)
  - Server status and health checks
- MCP Resources for database and table metadata

[0.1.0]: https://github.com/daedalus/mcp-mysql-connector/releases/tag/v0.1.0
