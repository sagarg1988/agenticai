from django.db import connection

class DBQueryTool:
    def __init__(self):
        pass

    def run(self, args, session_id=None):
        sql = args.get("sql")
        params = args.get("params", [])
        if not sql or ";" in sql:
            raise ValueError("Only safe single-statement queries allowed")
        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            cols = [c[0] for c in cursor.description] if cursor.description else []
            rows = cursor.fetchall()
            return {"columns": cols, "rows": rows}
