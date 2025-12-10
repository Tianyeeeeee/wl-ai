# app/db.py
import os
import pymysql
from dbutils.pooled_db import PooledDB
from dotenv import load_dotenv

load_dotenv()


class DBManager:
    _instance = None
    # 排除系统库，加快扫描速度
    SYSTEM_DBS = {
        'information_schema', 'mysql', 'performance_schema', 'sys',
        'nacos', 'xxl_job', 'seata', 'quartz', 'sentinel'
    }

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DBManager, cls).__new__(cls)
            cls._instance.pools = {}
            cls._instance.conn_params = {
                'host': os.getenv("DB_HOST"),
                'port': int(os.getenv("DB_PORT", 3306)),
                'user': os.getenv("DB_USER"),
                'password': os.getenv("DB_PASSWORD"),
                'cursorclass': pymysql.cursors.DictCursor,
                'connect_timeout': 3  # 3秒连不上就跳过
            }
            # 初始化不阻塞，按需获取
        return cls._instance

    def _fetch_all_dbs(self):
        """获取所有业务数据库"""
        # 如果 .env 指定了，只连指定的
        config_db_names = os.getenv("DB_NAME", "")
        if config_db_names:
            return [n.strip() for n in config_db_names.split(",") if n.strip()]

        try:
            conn = pymysql.connect(**self.conn_params)
            with conn.cursor() as cursor:
                cursor.execute("SHOW DATABASES")
                all_dbs = [r['Database'] for r in cursor.fetchall()]
                return [db for db in all_dbs if db.lower() not in self.SYSTEM_DBS]
        except Exception as e:
            print(f"❌ [DB] 获取库列表失败: {e}")
            return []

    def get_connection(self, db_name: str):
        if db_name not in self.pools:
            self.pools[db_name] = PooledDB(
                creator=pymysql, maxconnections=5, mincached=1, blocking=True,
                database=db_name, **self.conn_params
            )
        return self.pools[db_name].connection()

    def get_all_tables_metadata(self) -> list:
        """
        全量扫描：循环所有库，获取所有表 DDL
        """
        results = []
        dbs = self._fetch_all_dbs()
        total = len(dbs)
        print(f"🔄 [DB Scan] 发现 {total} 个数据库，开始提取 Schema...")

        for idx, db_name in enumerate(dbs):
            # 打印进度，防止用户以为卡死
            print(f"  👉 [{idx + 1}/{total}] Scanning {db_name}...", end="", flush=True)

            try:
                conn = self.get_connection(db_name)
                with conn.cursor() as cursor:
                    cursor.execute("SET SESSION wait_timeout=5")
                    cursor.execute("SHOW TABLES")
                    tables = [list(r.values())[0] for r in cursor.fetchall()]

                    if not tables:
                        print(" (Empty)")
                        continue

                    # 为了演示速度，这里只扫每个库前 50 张表
                    # 生产环境请去掉 [:50]
                    scan_limit = tables[:50]

                    for table in scan_limit:
                        try:
                            # 获取建表语句 (这是 LLM 最爱吃的格式)
                            cursor.execute(f"SHOW CREATE TABLE `{table}`")
                            res = cursor.fetchone()
                            if res:
                                ddl_str = list(res.values())[1]
                                # 获取列名用于 embedding
                                cursor.execute(f"DESCRIBE `{table}`")
                                cols = [row['Field'] for row in cursor.fetchall()]

                                results.append({
                                    "database": db_name,
                                    "table": table,
                                    "columns": ",".join(cols),
                                    "ddl_str": ddl_str
                                })
                        except:
                            continue
                conn.close()
                print(f" ✅ ({len(scan_limit)} tables)")
            except Exception as e:
                print(f" ❌ Skip ({e})")
                continue

        return results