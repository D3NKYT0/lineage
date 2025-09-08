# Documentation for apps.lineage.server

## Overview

The `apps.lineage.server` app is responsible for integrating Django with the Lineage 2 (L2) server database, allowing the web application to access, query, and manipulate game data in real time, without mixing Django data with L2 data.

---

## App Structure

- **models.py**: Django models for settings, service prices, supporters, etc. (site data, not L2 data)
- **database.py**: `LineageDB` class for connecting and operating on the L2 database (MySQL), using SQLAlchemy.
- **querys/**: Various files with SQL queries and utility classes to access L2 data (e.g., characters, clans, rankings, etc).
- **views/**: Django endpoints that expose L2 data to the frontend or APIs.
- **utils/**: Utilities, cache, etc.

---

## The L2 Database

The L2 database is a separate MySQL database, with tables such as `characters`, `accounts`, `clan_data`, `castle`, etc. It is not managed by the Django ORM, but is accessed directly via raw SQL.

- **Connection**: Made via SQLAlchemy, using environment variables for host, user, password, etc.
- **Main class**: `LineageDB` (singleton, thread-safe)
- **Operations**: select, insert, update, delete, execute_raw, with optional cache.
- **Usage example**:
  ```python
  from apps.lineage.server.database import LineageDB
  result = LineageDB().select("SELECT * FROM characters WHERE char_name = :name", {"name": "Hero"})
  ```

---

## Django x L2 Database Relationship

- **Django ORM**: Used only for site data (users, settings, purchases, etc).
- **L2 Database**: Accessed via raw SQL, without Django models, to ensure performance and compatibility with the game server.
- **Integration**: Utility functions and Django endpoints use `LineageDB` to fetch L2 data and display it on the site (e.g., rankings, castle status, online characters, etc).
- **Endpoint example**:
  ```python
  # views/server_views.py
  @endpoint_enabled('top_level')
  @safe_json_response
  def top_level(request):
      limit = int(request.GET.get("limit", 10))
      return LineageStats.top_level(limit=limit)
  ```
  Here, `LineageStats.top_level` executes an SQL query on the L2 database and returns the character ranking by level.

---

## Example Flow

1. User accesses a ranking page on the site.
2. Django calls a utility function (e.g., `LineageStats.top_level`) that executes an SQL query on the L2 database via `LineageDB`.
3. The result is returned and displayed on the frontend.

---

## Advantages of this approach
- **Isolation**: Game and site data remain separate, avoiding conflicts and making maintenance easier.
- **Performance**: Optimized queries run directly on the L2 database.
- **Flexibility**: Possible to adapt to different L2 database versions (acis, essence, lucera, etc) just by changing the queries.

---

## Notes
- Access to the L2 database can be disabled via the environment variable (`LINEAGE_DB_ENABLED`).
- Internal cache reduces load on repeated queries.
- Changes to the L2 database should be made carefully to avoid affecting the game server. 