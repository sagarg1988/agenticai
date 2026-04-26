"""
Database query tool — executes parameterised read-only SQL queries.

TODO: restrict to a read-only DB user with limited schema permissions.
TODO: add query allow-listing to prevent arbitrary SQL execution.
"""

from __future__ import annotations

import logging
from typing import Any

from agenticai.tools.fn_registry import BaseTool

logger = logging.getLogger(__name__)

MAX_ROWS = 100  # hard cap to prevent oversized result sets


class DBQueryTool(BaseTool):
    name = "db_query"

    def run(self, inputs: dict[str, Any]) -> list[dict]:
        from django.db import connection  # noqa: PLC0415

        sql: str = inputs.get("sql", "")
        params: list = inputs.get("params", [])

        # TODO: validate SQL is SELECT only (allow-list or query parser)
        logger.info("DBQueryTool.run", extra={"sql": sql})

        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            columns = [col[0] for col in (cursor.description or [])]
            rows = cursor.fetchmany(MAX_ROWS)
            return [dict(zip(columns, row)) for row in rows]
