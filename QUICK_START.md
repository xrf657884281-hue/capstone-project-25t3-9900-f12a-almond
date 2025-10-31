# 🚀 快速启动指南 - Quick Start Guide

## 📋 首次安装（只需要执行一次）

### Step 1: 进入项目目录
```bash
cd /path/to/capstone-project-25t3-9900-f12a-almond
# 或者如果已经克隆了项目，直接进入
cd 9900final
```

### Step 2: 后端自动安装（推荐）
```bash
cd backend
chmod +x setup.sh
./setup.sh
```

**或者手动安装：**
```bash
cd backend
mkdir -p logs
pip3 install -r requirements.txt
python3 -m spacy download en_core_web_sm
pip3 install tavily-python
python3 <<EOF
import nltk
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)
EOF
```

### Step 3: 创建 .env 文件（必须！）
```bash
cd backend
cat > .env <<EOF
OPENAI_API_KEY=你的openai_api_key
TAVILY_API_KEY=你的tavily_api_key（可选）
MONGODB_URL=mongodb://localhost:27017
LOG_LEVEL=INFO
LOG_FILE=logs/fakenews.log
EOF
```

**⚠️ 重要：** 请把 `你的openai_api_key` 替换成真实的 API key！

### Step 4: 前端安装
```bash
# 回到项目根目录
cd ..
npm install
```

---

## 🎯 日常运行（每次使用）

**需要打开 2 个终端窗口**

### 终端 1 - 启动后端
```bash
cd /path/to/9900final/backend
python3 main.py
```

**等待看到：**
```
✅ Detection service initialized
✅ Generation service initialized
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**✅ 成功标志：** 看到 `Application startup complete` 且没有错误

---

### 终端 2 - 启动前端
```bash
cd /path/to/9900final
npm run dev
```

**等待看到：**
```
VITE v7.1.9  ready in XXXX ms
➜  Local:   http://localhost:5173/
```

**✅ 成功标志：** 看到 `Local: http://localhost:XXXX/`

---

## 🌐 访问网页

打开浏览器，访问：**http://localhost:5173**（或显示的端口号）

---

## ⚠️ 常见问题

### 问题1: 端口被占用
```bash
# macOS/Linux - 查看占用8000端口的进程
lsof -ti :8000 | xargs kill

# 或者查找其他端口
lsof -ti :5173 | xargs kill
```

### 问题2: 缺少 .env 文件
```bash
cd backend
# 如果没有.env文件，创建它
cat > .env <<EOF
OPENAI_API_KEY=你的key
TAVILY_API_KEY=你的key
MONGODB_URL=mongodb://localhost:27017
LOG_LEVEL=INFO
LOG_FILE=logs/fakenews.log
EOF
```

### 问题3: spaCy模型未安装
```bash
python3 -m spacy download en_core_web_sm
```

### 问题4: 模块找不到
```bash
cd backend
pip3 install -r requirements.txt
pip3 install tavily-python
```

---

## ✅ 验证是否正常运行

### 测试后端
```bash
curl http://localhost:8000/health
```
应该返回：`{"status":"healthy",...}`

### 测试前端
打开浏览器：http://localhost:5173

如果能看到页面，说明运行成功！

---

## 📝 完整命令清单（复制粘贴用）

### 首次安装（一次性）
```bash
# 1. 进入项目
cd ~/Desktop/9900final  # 或你的项目路径

# 2. 后端安装
cd backend
chmod +x setup.sh && ./setup.sh

# 3. 创建.env（必须手动添加API keys）
cat > .env <<EOF
OPENAI_API_KEY=替换成你的key
TAVILY_API_KEY=替换成你的key
MONGODB_URL=mongodb://localhost:27017
LOG_LEVEL=INFO
LOG_FILE=logs/fakenews.log
EOF

# 4. 前端安装
cd ..
npm install
```

### 日常运行
```bash
# 终端1：后端
cd ~/Desktop/9900final/backend
python3 main.py

# 终端2：前端（新开一个终端）
cd ~/Desktop/9900final
npm run dev
```

---

## 🛑 停止服务

在运行的终端中按：**`Ctrl + C`**

---

## 📞 如果还有问题

1. 检查 Python 版本：`python3 --version` （需要 3.8+）
2. 检查 Node 版本：`node --version` （需要 16+）
3. 查看错误日志：`backend/logs/fakenews.log`
4. 查看终端错误信息

