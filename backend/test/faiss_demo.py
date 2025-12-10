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

def demo_faiss_basic():
    """FAISS基础使用演示"""
    print("🚀 FAISS向量检索演示开始")
    
    # 创建向量数据
    dimension = 64  # 使用较小的维度便于演示
    nb = 1000   # 数据库大小
    nq = 5      # 查询数量

    # 生成随机向量
    print("🔢 生成随机向量数据...")
    np.random.seed(1234)  # 固定随机种子便于复现
    xb = np.random.random((nb, dimension)).astype('float32')
    xq = np.random.random((nq, dimension)).astype('float32')
    print(xb, 'xb')
    print(xq, 'xq')

    # 方法1：暴力搜索 (精确搜索)
    print("🔍 方法1: 暴力搜索 (精确搜索)")
    index_flat = faiss.IndexFlatL2(dimension)
    index_flat.add(xb)
    D, I = index_flat.search(xq, 4)  # 返回4个最近邻
    print(f"   搜索结果形状: {D.shape}")  # (查询数, 最近邻数)
    print(f"   最近邻距离: {D[0][:3]}")
    print(f"   最近邻索引: {I[0][:3]}")

    # 方法2：IVF索引 (近似搜索，速度快)
    print("🔍 方法2: IVF索引 (近似搜索)")
    nlist = 50  # 聚类中心数
    quantizer = faiss.IndexFlatL2(dimension)
    index_ivf = faiss.IndexIVFFlat(quantizer, dimension, nlist)
    
    # 训练阶段
    print("   训练索引...")
    index_ivf.train(xb)
    
    # 添加数据
    print("   添加数据...")
    index_ivf.add(xb)
    
    # 搜索
    D, I = index_ivf.search(xq, 4)
    print(f"   搜索结果形状: {D.shape}")
    print(f"   最近邻距离: {D[0][:3]}")
    print(f"   最近邻索引: {I[0][:3]}")

    # 方法3：HNSW索引 (图搜索，高精度)
    print("🔍 方法3: HNSW索引 (图搜索)")
    index_hnsw = faiss.IndexHNSWFlat(dimension, 32)
    
    print("   添加数据...")
    index_hnsw.add(xb)
    
    # 搜索
    D, I = index_hnsw.search(xq, 4)
    print(f"   搜索结果形状: {D.shape}")
    print(f"   最近邻距离: {D[0][:3]}")
    print(f"   最近邻索引: {I[0][:3]}")
    
    print("✅ FAISS演示完成")

if __name__ == "__main__":
    demo_faiss_basic()