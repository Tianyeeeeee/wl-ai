import json
import os
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

from typing import List, Dict
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

class RAGEngine:
    def __init__(self, documents_path: str = "./documents.json"):
        print("🚀 初始化 RAG 引擎...")
        
        # 加载文档
        self.documents = self._load_documents(documents_path)
        print(f"📚 加载了 {len(self.documents)} 个文档")
        
        # 初始化向量模型
        print("🧠 加载向量模型...")
        model_path = "./models/paraphrase-multilingual-MiniLM-L12-v2"
        if os.path.exists(model_path):
            print("📂 使用本地模型")
            # 使用相对路径而不是绝对路径，避免中文路径问题
            self.model = SentenceTransformer(model_path)
        else:
            raise FileNotFoundError(f"本地模型文件未找到: {model_path}。请确保模型已下载到指定位置。")
        print("✅ 模型加载完成")
        
        # 构建向量索引
        self._build_vector_index()
        
    def _load_documents(self, path: str) -> List[Dict]:
        """加载文档数据"""
        # 尝试多个路径
        possible_paths = [
            path,
            './documents.json',
        ]
        
        for file_path in possible_paths:
            try:
                if os.path.exists(file_path):
                    print(f"✅ 找到文档文件: {file_path}")
                    with open(file_path, 'r', encoding='utf-8') as f:
                        documents = json.load(f)
                    print(f"📄 成功加载 {len(documents)} 个文档")
                    return documents
            except Exception as e:
                print(f"⚠️ 尝试路径 {file_path} 失败: {e}")
                continue
        
        # 如果找不到文件，使用默认文档
        print("❌ 未找到文档文件，使用默认文档")
        return self._get_default_documents()
    
    def _get_default_documents(self) -> List[Dict]:
        """获取默认文档"""
        return [
            {
                "title": "人工智能简介",
                "content": "人工智能（Artificial Intelligence，AI）是指由人工制造出来的系统所表现出来的智能。人工智能的核心问题包括推理、知识、规划、学习、交流、感知、移动和操作物体的能力等。AI技术已经广泛应用于医疗诊断、金融风控、自动驾驶等领域。",
                "metadata": {"category": "technology", "source": "wikipedia"}
            },
            {
                "title": "机器学习基础",
                "content": "机器学习是人工智能的一个分支，它使计算机能够从数据中学习并做出预测或决策，而无需明确编程。主要类型包括监督学习、无监督学习和强化学习。监督学习使用标记数据进行训练，无监督学习发现数据中的隐藏模式，强化学习通过奖励机制学习最优策略。",
                "metadata": {"category": "technology", "source": "educational"}
            },
            {
                "title": "深度学习发展",
                "content": "深度学习是机器学习的一个子集，使用多层神经网络来模拟人脑的工作方式。近年来在图像识别、自然语言处理等领域取得了突破性进展。卷积神经网络(CNN)擅长处理图像数据，循环神经网络(RNN)适合序列数据处理，Transformer架构则革新了自然语言处理领域。",
                "metadata": {"category": "technology", "source": "research"}
            }
        ]
    
    def _build_vector_index(self):
        """构建向量索引"""
        print("🏗️ 构建向量索引...")
        
        # 获取所有文档内容
        texts = [doc['content'] for doc in self.documents]
        
        # 生成向量
        print("🔢 生成文档向量...")
        embeddings = self.model.encode(texts)
        
        # 创建FAISS索引
        dimension = embeddings.shape[1]
        self.index = faiss1.IndexFlatIP(dimension)  # 使用内积相似度
        
        # 归一化向量并添加到索引
        faiss1.normalize_L2(embeddings)
        self.index.add(embeddings.astype('float32'))
        
        print("✅ 向量索引构建完成")
    
    def search(self, query: str, top_k: int = 5, threshold: float = 0.5) -> List[Dict]:
        """搜索相关文档"""
        print(f"🔍 搜索查询: '{query}'")
        
        # 生成查询向量
        query_embedding = self.model.encode([query])
        faiss1.normalize_L2(query_embedding)
        
        # 搜索
        similarities, indices = self.index.search(query_embedding.astype('float32'), top_k)
        
        # 处理结果
        results = []
        for i, (similarity, idx) in enumerate(zip(similarities[0], indices[0])):
            if similarity >= threshold and idx < len(self.documents):
                doc = self.documents[idx]
                results.append({
                    'id': int(idx),
                    'content': doc['content'],
                    'title': doc['title'],
                    'similarity': float(similarity),
                    'metadata': doc.get('metadata', {})
                })
        
        print(f"🎯 找到 {len(results)} 个相关文档")
        return results
    
    def generate_answer(self, question: str, documents: List[Dict]) -> str:
        """生成答案（简化版）"""
        if not documents:
            return "抱歉，我没有找到相关的信息来回答您的问题。"
        
        # 构建上下文
        context_parts = []
        for doc in documents[:3]:  # 只使用最相关的3个文档
            context_parts.append(f"【{doc['title']}】{doc['content']}")
        
        context = "\n\n".join(context_parts)
        
        # 生成答案模板
        answer = f"根据相关文档信息回答您的问题：\n\n{context}\n\n以上信息来自相关文档，希望对您有帮助。"
        
        return answer