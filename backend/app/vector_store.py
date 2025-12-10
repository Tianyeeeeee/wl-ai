# app/vector_store.py
import faiss
import json
import os
from sentence_transformers import SentenceTransformer
from typing import List, Dict


class VectorStore:
    _instance = None
    DATA_DIR = "./data"
    # 三种类型的索引：表结构、文档、历史 SQL
    FILES = {"ddl": "index_ddl", "doc": "index_doc", "sql": "index_sql"}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VectorStore, cls).__new__(cls)
            if not os.path.exists(cls.DATA_DIR): os.makedirs(cls.DATA_DIR)

            # 加载 Embedding 模型 (Vanna 默认也用这类模型)
            # 第一次运行会下载，可能稍慢
            cls._instance.model = SentenceTransformer('./models/paraphrase-multilingual-MiniLM-L12-v2')

            cls._instance.indices = {}
            cls._instance.data_store = {}
            cls._instance._load_indices()
        return cls._instance

    def _load_indices(self):
        """加载本地索引"""
        for key in self.FILES:
            self.data_store[key] = []
            path = os.path.join(self.DATA_DIR, f"{self.FILES[key]}.json")
            if os.path.exists(path):
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        self.data_store[key] = json.load(f)
                except:
                    pass
            self._rebuild_index(key)

    def _rebuild_index(self, key):
        """构建 FAISS 向量索引"""
        data = self.data_store[key]
        if not data:
            self.indices[key] = None
            return

        # 提取用于 Embedding 的文本
        texts = [i.get('emb_text', '') for i in data]
        if not texts: return

        emb = self.model.encode(texts)
        idx = faiss.IndexFlatIP(emb.shape[1])
        faiss.normalize_L2(emb)
        idx.add(emb.astype('float32'))
        self.indices[key] = idx

    def add_training_data(self, dtype: str, content: dict):
        """
        核心训练方法：将 Schema/Doc/SQL 存入知识库
        """
        if dtype not in self.FILES: return

        # 1. 构造 Embedding 文本 (决定了检索的准确度)
        if dtype == 'ddl':
            # 格式：Database.Table + Columns
            # 这样用户搜 "lpcarnet.car_base_info" 或 "车型表" 都能搜到
            db = content.get('database', 'unknown')
            tb = content.get('table', 'unknown')
            cols = content.get('columns', '')
            content['emb_text'] = f"DB: {db}, Table: {tb}, Columns: {cols}"

            # 存储时，把 Database 信息注入到 DDL 字符串中，方便 LLM 识别
            origin_ddl = content.get('ddl_str', '')
            content['ddl_str'] = f"/* Database: {db} */\n{origin_ddl}"

        elif dtype == 'sql':
            content['emb_text'] = content['question']  # 根据问题检索 SQL
        else:
            content['emb_text'] = content['doc']

        # 2. 查重 (防止重复训练)
        for x in self.data_store[dtype]:
            if x['emb_text'] == content['emb_text']: return

        # 3. 存储并重建索引
        self.data_store[dtype].append(content)

        with open(os.path.join(self.DATA_DIR, f"{self.FILES[dtype]}.json"), 'w', encoding='utf-8') as f:
            json.dump(self.data_store[dtype], f, ensure_ascii=False, indent=2)

        self._rebuild_index(dtype)

    def retrieve(self, query: str, top_k=8) -> Dict[str, List[str]]:
        """
        语义检索：Vanna 模式的核心
        只返回 Top-K 相关的表结构，节省 Token
        """
        res = {"ddl": [], "doc": [], "sql": []}
        if not any(self.indices.values()): return res

        q_emb = self.model.encode([query])
        faiss.normalize_L2(q_emb)

        for key, idx in self.indices.items():
            if not idx: continue

            # DDL 查多一点 (top_k)，文档和 SQL 查少一点
            k = top_k if key == 'ddl' else 3
            D, I = idx.search(q_emb.astype('float32'), min(k, len(self.data_store[key])))

            for i in I[0]:
                if i < len(self.data_store[key]):
                    item = self.data_store[key][i]
                    if key == 'ddl':
                        res['ddl'].append(item.get('ddl_str', ''))
                    elif key == 'doc':
                        res['doc'].append(item.get('doc', ''))
                    elif key == 'sql':
                        res['sql'].append(f"Q: {item.get('question')}\nA: {item.get('sql')}")
        return res