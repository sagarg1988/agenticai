"""
DB Query tool — executes read-only SQL queries against the application database.

TODO:
- Restrict to read-only transactions (SET TRANSACTION READ ONLY).
- Validate / whitelist allowed tables to prevent data exfiltration.
- Add query timeout to prevent long-running queries.
"""
from __future__ import annotations

import logging

from django.db import connection

from tools.registry import register

logger = logging.getLogger(__name__)


@register("db_query")
def db_query(sql: str, params: list | None = None) -> list[dict]:
    """
    Execute a read-only SQL query and return rows as a list of dicts.

    Args:
        sql: The SQL query string (SELECT only).
        params: Optional list of positional query parameters.

    Returns:
        List of row dicts.
    """
    logger.info("db_query sql=%r", sql[:200])
    # TODO: enforce read-only mode and table whitelist
    if not sql.strip().upper().startswith("SELECT"):
        raise ValueError("Only SELECT queries are permitted.")

    with connection.cursor() as cursor:
        cursor.execute(sql, params or [])
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
