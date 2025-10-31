# 🚀 完整安装指南 - Setup Guide

这个指南确保所有团队成员能够在自己的电脑上正常运行项目。

## ⚠️ 常见问题

如果项目在你的电脑上能运行，但在组员的电脑上不能运行，可能是以下原因：

### 1. 缺少 logs 目录
**错误**: `FileNotFoundError: logs/fakenews.log`

**解决方法**:
```bash
cd backend
mkdir -p logs
```

### 2. 缺少 spaCy 模型
**错误**: `OSError: Can't find model 'en_core_web_sm'`

**解决方法**:
```bash
python3 -m spacy download en_core_web_sm
```

### 3. 缺少 .env 文件
**错误**: API连接失败，服务无法启动

**解决方法**:
```bash
cd backend
# 如果存在 .env.example，复制它
cp .env.example .env
# 或者手动创建 .env 文件，添加以下内容：
```

创建 `backend/.env` 文件：
```
OPENAI_API_KEY=your_openai_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
MONGODB_URL=mongodb://localhost:27017
LOG_LEVEL=INFO
LOG_FILE=logs/fakenews.log
```

### 4. NLTK 数据未下载
**错误**: NLTK相关功能报错

**解决方法**:
```bash
python3 <<EOF
import nltk
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger')
EOF
```

### 5. 系统依赖问题

#### macOS:
```bash
# 确保有 Xcode Command Line Tools
xcode-select --install
```

#### Linux:
```bash
# 安装编译工具
sudo apt-get update
sudo apt-get install build-essential python3-dev
```

#### Windows:
- 安装 Visual Studio Build Tools
- 或者使用 WSL2

## 📋 完整安装步骤

### 方式1: 使用自动安装脚本（推荐）

```bash
cd backend
chmod +x setup.sh
./setup.sh
```

### 方式2: 手动安装

#### Step 1: 克隆项目
```bash
git clone https://github.com/unsw-cse-comp99-3900/capstone-project-25t3-9900-f12a-almond.git
cd capstone-project-25t3-9900-f12a-almond
```

#### Step 2: 后端设置
```bash
cd backend

# 创建必要的目录
mkdir -p logs

# 安装Python依赖
pip3 install -r requirements.txt

# 下载spaCy模型
python3 -m spacy download en_core_web_sm

# 下载NLTK数据
python3 <<EOF
import nltk
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)
EOF

# 创建.env文件（如果不存在）
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

#### Step 3: 前端设置
```bash
# 从项目根目录
cd ..
npm install
```

#### Step 4: 启动服务
```bash
# 终端1: 启动后端
cd backend
python3 main.py

# 终端2: 启动前端
npm run dev
```

## 🔍 验证安装

### 检查后端
```bash
curl http://localhost:8000/health
```

应该返回:
```json
{
  "status": "healthy",
  "services": {
    "detection": true,
    "improved_detection": true,
    "generation": true
  }
}
```

### 检查前端
打开浏览器访问: http://localhost:5173 (或5174)

## 🐛 故障排除

### 问题: 端口被占用
```bash
# macOS/Linux
lsof -ti :8000 | xargs kill
lsof -ti :5173 | xargs kill

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### 问题: 权限错误
```bash
chmod +x backend/setup.sh
chmod +x backend/start.sh
```

### 问题: Python版本不对
需要 Python 3.8+
```bash
python3 --version
# 如果不是 3.8+，需要安装或更新
```

### 问题: Node.js版本不对
需要 Node.js 16+
```bash
node --version
# 如果不是 16+，需要安装或更新
```

## 📦 所有需要的依赖清单

### Python包 (requirements.txt)
- fastapi==0.104.1
- uvicorn==0.24.0
- openai>=1.12.0
- transformers==4.35.0
- torch>=2.2.0
- torchvision>=0.17.0
- pillow==10.0.1
- numpy==1.24.3
- scikit-learn==1.3.0
- spacy==3.7.0
- textstat==0.7.3
- requests==2.31.0
- pymongo==4.6.0
- pydantic==2.4.2
- python-multipart==0.0.6
- nltk>=3.8.0
- python-dotenv>=1.0.0

### spaCy模型
- en_core_web_sm

### NLTK数据
- punkt
- stopwords
- averaged_perceptron_tagger

### 系统依赖
- Python 3.8+
- Node.js 16+
- Git
- (可选) MongoDB

## 💡 快速检查清单

在运行项目前，确保：

- [ ] Python 3.8+ 已安装
- [ ] Node.js 16+ 已安装
- [ ] `backend/logs/` 目录存在
- [ ] `backend/.env` 文件存在且有正确的API keys
- [ ] spaCy模型已下载: `python3 -m spacy download en_core_web_sm`
- [ ] NLTK数据已下载
- [ ] Python依赖已安装: `pip3 install -r requirements.txt`
- [ ] Node依赖已安装: `npm install`

## 📞 需要帮助？

如果按照以上步骤仍然无法运行，请检查：
1. 错误日志 (`backend/logs/fakenews.log`)
2. 终端输出
3. 浏览器控制台（前端问题）
4. 系统版本是否匹配要求

