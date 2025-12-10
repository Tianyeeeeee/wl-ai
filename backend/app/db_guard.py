# app/db_guard.py
import re


class SQLGuard:
    FORBIDDEN_KEYWORDS = [
        "DROP ", "DELETE ", "UPDATE ", "INSERT ", "ALTER ",
        "GRANT ", "REVOKE ", "TRUNCATE ", "CREATE "
    ]

    @staticmethod
    def validate(sql: str) -> str:
        sql_upper = sql.upper().strip()

        # 1. 黑名单检查
        for kw in SQLGuard.FORBIDDEN_KEYWORDS:
            if kw in sql_upper:
                raise ValueError(f"SECURITY ALERT: Keyword '{kw}' forbidden.")

        # 2. 智能 LIMIT (修复点：只针对 SELECT)
        # 只有以 SELECT 开头，且没有 LIMIT，且不是聚合查询时，才加 LIMIT
        if sql_upper.startswith("SELECT") and "LIMIT " not in sql_upper:
            is_agg = any(x in sql_upper for x in ["COUNT(", "SUM(", "AVG(", "MAX(", "MIN("])
            if not is_agg:
                return sql + " LIMIT 100"

        return sql