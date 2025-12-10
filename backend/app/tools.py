# app/tools.py
import json
import re
import ast
import datetime
import decimal
from typing import Dict, Any
from .db import DBManager


class ToolManager:
    def __init__(self):
        self.db = DBManager()

    def get_definitions(self):
        return [
            {
                "type": "function",
                "function": {
                    "name": "execute_sql",
                    "description": "Execute SQL. Ensure table names are prefixed with database name (e.g. db.table).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "SQL query"}
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "generate_chart",
                    "description": "Visualize data.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "chart_type": {"type": "string", "enum": ["bar", "line", "pie"]},
                            "x_key": {"type": "string"},
                            "y_key": {"type": "string"},
                            "title": {"type": "string"}
                        },
                        "required": ["chart_type", "x_key", "y_key"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "execute_python",
                    "description": "Run python code for analysis.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "code": {"type": "string"}
                        },
                        "required": ["code"]
                    }
                }
            }
        ]

    def parse_args(self, raw_args: str) -> Dict[str, Any]:
        if not raw_args: return {}
        text = raw_args.strip()
        try:
            return json.loads(text)
        except:
            pass
        try:
            return ast.literal_eval(text)
        except:
            pass
        return {}

    def _sanitize(self, data: Any) -> Any:
        if isinstance(data, list): return [self._sanitize(i) for i in data]
        if isinstance(data, dict): return {k: self._sanitize(v) for k, v in data.items()}
        if isinstance(data, (datetime.datetime, datetime.date)): return data.isoformat()
        if isinstance(data, decimal.Decimal): return float(data)
        if isinstance(data, bytes): return data.decode('utf-8', errors='ignore')
        return data

    def execute(self, tool_name, args):
        if tool_name != "execute_sql": return {"status": "error", "message": "Invalid call"}

        sql = args.get("query", "")

        # 随便连一个库，只要能执行 SQL 即可 (MySQL 支持跨库查询)
        dbs = self.db._fetch_all_dbs()
        target_db = dbs[0] if dbs else "mysql"

        print(f"⚡ [Exec] SQL: {sql[:100]}...")

        try:
            conn = self.db.get_connection(target_db)
            with conn.cursor() as cursor:
                cursor.execute(sql)
                res = cursor.fetchall()
                return {"status": "success", "data": self._sanitize(res)}
        except Exception as e:
            return {"status": "error", "message": f"SQL Error: {str(e)}"}
        finally:
            if 'conn' in locals() and conn: conn.close()