import numpy as np

# 先尝试导入faiss库
try:
    import faiss
    print("✅ FAISS库导入成功")
except ImportError as e:
    print("❌ FAISS库导入失败，请安装faiss库:")
    print("pip install faiss-cpu  # CPU版本")
    print("pip install faiss-gpu  # GPU版本（需要CUDA）")
    exit(1)

# 简单的手工向量编码函数（模拟真实的向量表示）
def simple_text_to_vector(text):
    """简单的文本转向量函数，用于演示"""
    # 这里我们手工构造一些有意义的向量
    # 实际应用中会使用BERT、Sentence-BERT等模型
    words = text.lower().split()
    vector = np.zeros(16, dtype='float32')  # 使用16维便于演示
    
    # 简单的词频统计 + 位置编码
    word_map = {
        'ai': 0, 'artificial': 0, 'intelligence': 1,
        'ml': 2, 'machine': 2, 'learning': 3,
        'dl': 4, 'deep': 4, 'neural': 5, 'network': 5,
        'computer': 6, 'science': 7, 'data': 8,
        'algorithm': 9, 'model': 10, 'training': 11,
        'python': 12, 'programming': 13, 'code': 14,
        'application': 15
    }
    
    for word in words:
        for key in word_map:
            if key in word:
                vector[word_map[key]] += 1.0
    
    # 归一化
    norm = np.linalg.norm(vector)
    if norm > 0:
        vector = vector / norm
    
    return vector

def demo_faiss_with_real_data():
    """使用真实数据的FAISS演示"""
    print("🚀 FAISS向量检索演示（真实数据版）")
    
    # 创建真实的文档数据
    database_documents = [
        "Artificial Intelligence is a branch of computer science",
        "Machine Learning algorithms can learn from data",
        "Deep Neural Networks are used in deep learning",
        "Python programming language is popular for AI development",
        "Data Science involves statistical analysis and machine learning",
        "Computer vision applications use neural networks",
        "Natural language processing is a subfield of AI",
        "Supervised learning requires labeled training data",
        "Reinforcement learning uses reward-based training",
        "Big data analytics helps business decision making"
    ]
    
    query_documents = [
        "What is artificial intelligence?",
        "How does machine learning work?",
        "Programming languages for AI development",
        "Applications of neural networks",
        "Data analysis techniques"
    ]
    
    dimension = 16  # 向量维度
    
    print("\n📚 数据库文档:")
    for i, doc in enumerate(database_documents):
        print(f"  [{i}] {doc}")
    
    print("\n❓ 查询问题:")
    for i, query in enumerate(query_documents):
        print(f"  [{i}] {query}")
    
    # 将文档转换为向量
    print("\n🔄 将文档转换为向量...")
    xb = np.array([simple_text_to_vector(doc) for doc in database_documents], dtype='float32')
    xq = np.array([simple_text_to_vector(query) for query in query_documents], dtype='float32')
    
    print(f"\n📊 向量形状:")
    print(f"   数据库向量 (xb): {xb.shape}")  # (10, 16) - 10个文档，16维向量
    print(f"   查询向量 (xq): {xq.shape}")   # (5, 16) - 5个查询，16维向量
    
    # 显示前几个向量示例
    print(f"\n📋 向量示例:")
    print(f"   文档0向量: {xb[0][:5]}...")  # 显示前5维
    print(f"   查询0向量: {xq[0][:5]}...")  # 显示前5维
    
    # 方法1：暴力搜索 (精确搜索)
    print("\n🔍 方法1: 暴力搜索 (精确搜索)")
    index_flat = faiss.IndexFlatL2(dimension)
    index_flat.add(xb)
    D, I = index_flat.search(xq, 3)  # 返回3个最近邻
    
    print(f"   搜索结果分析:")
    for i in range(len(query_documents)):
        query_text = query_documents[i]
        distances = D[i][:3]
        indices = I[i][:3]
        
        print(f"\n   查询: '{query_text}'")
        print(f"   最近邻:")
        for j, (idx, dist) in enumerate(zip(indices, distances)):
            print(f"     {j+1}. [{idx}] '{database_documents[idx]}' (距离: {dist:.3f})")
    
    # 方法2：IVF索引 (近似搜索)
    print("\n🔍 方法2: IVF索引 (近似搜索)")
    nlist = 3  # 聚类中心数
    quantizer = faiss.IndexFlatL2(dimension)
    index_ivf = faiss.IndexIVFFlat(quantizer, dimension, nlist)
    
    print("   训练索引...")
    index_ivf.train(xb)
    
    print("   添加数据...")
    index_ivf.add(xb)
    
    D, I = index_ivf.search(xq, 3)
    
    print(f"   搜索结果分析:")
    for i in range(len(query_documents)):
        query_text = query_documents[i]
        distances = D[i][:3]
        indices = I[i][:3]
        
        print(f"\n   查询: '{query_text}'")
        print(f"   最近邻:")
        for j, (idx, dist) in enumerate(zip(indices, distances)):
            print(f"     {j+1}. [{idx}] '{database_documents[idx]}' (距离: {dist:.3f})")
    
    print("\n✅ FAISS演示完成")

if __name__ == "__main__":
    demo_faiss_with_real_data()