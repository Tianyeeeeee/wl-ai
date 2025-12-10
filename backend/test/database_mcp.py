# database_mcp.py
import pymysql
import uvicorn
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from dbutils.pooled_db import PooledDB  # 引入连接池

load_dotenv()

app = FastAPI(title="Fast Database MCP")

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)

# === 🚀 优化 1: 数据库连接池 ===
# 初始化连接池，避免每次请求都重新连接
pool = PooledDB(
    creator=pymysql,
    maxconnections=10,  # 最大连接数
    mincached=2,  # 初始化时建立的连接数
    maxcached=5,
    blocking=True,
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT", 3306)),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME"),
    cursorclass=pymysql.cursors.DictCursor
)


def get_db_connection():
    return pool.connection()


class SQLRequest(BaseModel):
    query: str


# === 🚀 优化 2: 新增“获取全量数据库结构”接口 ===
# 让 Agent 启动时就读这个，以后就不用问“有哪些表”了
@app.get("/meta/full_schema")
def get_full_schema():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # 1. 查所有表
            cursor.execute("SHOW TABLES")
            tables = [list(row.values())[0] for row in cursor.fetchall()]

            schema_info = []
            # 2. 查每个表的字段 (限制只查前10个表，防止Token爆炸)
            for table in tables[:10]:
                cursor.execute(f"DESCRIBE `{table}`")
                cols = cursor.fetchall()
                col_str = ", ".join([f"{c['Field']}({c['Type']})" for c in cols])
                schema_info.append(f"Table: {table}\nColumns: {col_str}")

            return {
                "status": "success",
                "schema_summary": "\n\n".join(schema_info)
            }
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        conn.close()


# 保持原有的 execute_sql，去掉其他查表工具
@app.post("/tools/execute_sql")
def execute_sql(payload: SQLRequest):
    sql = payload.query.strip()
    if not sql.lower().startswith("select"):
        return {"status": "error", "message": "Only SELECT allowed"}

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            if "limit" not in sql.lower(): sql += " LIMIT 20"
            cursor.execute(sql)
            return {"status": "success", "data": cursor.fetchall()}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        conn.close()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3001)