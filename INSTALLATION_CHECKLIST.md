# ✅ 安装检查清单 - Installation Checklist

这个清单确保所有团队成员能够成功运行项目。

## 🔍 常见问题诊断

如果你的电脑可以运行，但组员的电脑不能，请检查以下每一项：

### ❌ 问题1: logs目录不存在
**错误信息**: `FileNotFoundError: [Errno 2] No such file or directory: 'logs/fakenews.log'`

**✅ 解决方法**:
```bash
cd backend
mkdir -p logs
# 或者运行
python3 main.py  # 新代码会自动创建logs目录
```

### ❌ 问题2: spaCy模型未安装
**错误信息**: `OSError: Can't find model 'en_core_web_sm'`

**✅ 解决方法**:
```bash
python3 -m spacy download en_core_web_sm
```

### ❌ 问题3: .env文件不存在
**错误信息**: API连接失败，`OPENAI_API_KEY not set`

**✅ 解决方法**:
```bash
cd backend
# 创建.env文件
cat > .env <<EOF
OPENAI_API_KEY=your_openai_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
MONGODB_URL=mongodb://localhost:27017
LOG_LEVEL=INFO
LOG_FILE=logs/fakenews.log
EOF
# 然后更新API keys
```

### ❌ 问题4: NLTK数据未下载
**错误信息**: NLTK相关功能报错

**✅ 解决方法**:
```bash
python3 <<EOF
import nltk
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)
EOF
```

### ❌ 问题5: Tavily包未安装
**错误信息**: `ImportError: No module named 'tavily'`

**✅ 解决方法**:
```bash
pip3 install tavily-python
```

### ❌ 问题6: Python包版本不匹配
**错误信息**: 各种导入或运行错误

**✅ 解决方法**:
```bash
cd backend
pip3 install -r requirements.txt --force-reinstall
```

### ❌ 问题7: Node.js依赖未安装
**错误信息**: 前端无法启动

**✅ 解决方法**:
```bash
npm install
```

## 📋 完整安装步骤（给新组员）

### Step 1: 检查系统要求
```bash
# 检查Python版本（需要3.8+）
python3 --version

# 检查Node.js版本（需要16+）
node --version

# 检查npm
npm --version
```

### Step 2: 克隆项目
```bash
git clone https://github.com/unsw-cse-comp99-3900/capstone-project-25t3-9900-f12a-almond.git
cd capstone-project-25t3-9900-f12a-almond
```

### Step 3: 后端设置（推荐使用自动脚本）
```bash
cd backend
chmod +x setup.sh
./setup.sh
```

**或者手动安装**:
```bash
cd backend

# 1. 创建logs目录
mkdir -p logs

# 2. 安装Python依赖
pip3 install -r requirements.txt

# 3. 下载spaCy模型
python3 -m spacy download en_core_web_sm

# 4. 下载NLTK数据
python3 <<EOF
import nltk
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)
EOF

# 5. 安装Tavily（如果使用事实验证）
pip3 install tavily-python

# 6. 创建.env文件
if [ ! -f .env ]; then
    cat > .env <<ENVEOF
OPENAI_API_KEY=your_openai_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=fakenews_db
LOG_LEVEL=INFO
LOG_FILE=logs/fakenews.log
ENVEOF
    echo "⚠️  请更新 .env 文件中的 API keys"
fi
```

### Step 4: 前端设置
```bash
# 从项目根目录
npm install
```

### Step 5: 启动服务

**终端1 - 后端**:
```bash
cd backend
python3 main.py
```

**终端2 - 前端**:
```bash
npm run dev
```

## 🔍 验证安装

### 检查后端
```bash
curl http://localhost:8000/health
```
应该返回健康状态。

### 检查前端
打开浏览器访问: http://localhost:5173

## 📝 所有依赖清单

### Python包（从requirements.txt）
- ✅ fastapi==0.104.1
- ✅ uvicorn==0.24.0
- ✅ openai>=1.12.0
- ✅ transformers==4.35.0
- ✅ torch>=2.2.0
- ✅ torchvision>=0.17.0
- ✅ pillow==10.0.1
- ✅ numpy==1.24.3
- ✅ scikit-learn==1.3.0
- ✅ spacy==3.7.0
- ✅ textstat==0.7.3
- ✅ requests==2.31.0
- ✅ pymongo==4.6.0
- ✅ pydantic==2.4.2
- ✅ python-multipart==0.0.6
- ✅ nltk>=3.8.0
- ✅ python-dotenv>=1.0.0
- ✅ **tavily-python** (需要额外安装，不在requirements.txt中)

### spaCy模型（需要单独下载）
- ✅ en_core_web_sm

### NLTK数据（需要单独下载）
- ✅ punkt
- ✅ stopwords
- ✅ averaged_perceptron_tagger

### 系统依赖
- ✅ Python 3.8+
- ✅ Node.js 16+
- ✅ Git
- ✅ (可选) MongoDB

### 文件/目录
- ✅ `backend/logs/` 目录
- ✅ `backend/.env` 文件（带API keys）
- ✅ `node_modules/` (npm install会自动创建)

## 🚨 必须执行的操作

在新电脑上首次运行前，**必须**执行：

1. ✅ `cd backend && mkdir -p logs`
2. ✅ `pip3 install -r requirements.txt`
3. ✅ `python3 -m spacy download en_core_web_sm`
4. ✅ `pip3 install tavily-python` (如果使用事实验证)
5. ✅ 创建 `backend/.env` 文件并填入API keys
6. ✅ `npm install` (在项目根目录)

## 💡 快速诊断命令

```bash
# 检查所有必要文件是否存在
cd backend
test -d logs && echo "✅ logs目录存在" || echo "❌ logs目录缺失"
test -f .env && echo "✅ .env文件存在" || echo "❌ .env文件缺失"
python3 -m spacy info en_core_web_sm && echo "✅ spaCy模型已安装" || echo "❌ spaCy模型未安装"
python3 <<EOF
import nltk
try:
    nltk.data.find('tokenizers/punkt')
    print("✅ NLTK punkt已安装")
except:
    print("❌ NLTK punkt未安装")
EOF
python3 <<EOF
try:
    import tavily
    print("✅ Tavily包已安装")
except:
    print("❌ Tavily包未安装")
EOF
```

