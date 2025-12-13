# Backend Setup

## 创建虚拟环境
```bash
python -m venv .venv
```

## 激活虚拟环境
```bash
# Windows cmd
.venv\Scripts\activate

# Windows PowerShell
.venv\Scripts\Activate.ps1
```

## 升级pip
```bash
python -m pip install --upgrade pip setuptools wheel
```

## 安装依赖（使用国内镜像源避免编译问题）
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

## 生成依赖文件
```bash
pip freeze > requirements.txt
```

## 运行应用
```bash
python main.py
```