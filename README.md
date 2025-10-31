# 🚀 Fake News Detection System

A comprehensive AI-powered fake news detection and generation system built with React, TypeScript, FastAPI, and multiple ML models.

## ⚡ Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- Git

### 🛠️ Setup Instructions

#### 1. Clone Repository
```bash
git clone https://github.com/unsw-cse-comp99-3900/capstone-project-25t3-9900-f12a-almond.git
cd capstone-project-25t3-9900-f12a-almond
```

#### 2. Backend Setup
```bash
cd backend

# Option 1: Use automatic setup script (Recommended)
chmod +x setup.sh
./setup.sh

# Option 2: Manual setup
# Create logs directory
mkdir -p logs

# Install Python dependencies
pip3 install -r requirements.txt

# Download spaCy English model (Required)
python3 -m spacy download en_core_web_sm

# Download NLTK data (Required)
python3 <<EOF
import nltk
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)
EOF

# Create .env file with API keys
# Copy from .env.example or create manually
if [ ! -f .env ]; then
    cat > .env <<ENVEOF
OPENAI_API_KEY=your_openai_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
MONGODB_URL=mongodb://localhost:27017
LOG_LEVEL=INFO
LOG_FILE=logs/fakenews.log
ENVEOF
    echo "⚠️  Please update .env file with your API keys"
fi

# Start backend server
python3 main.py
```

**⚠️ Important**: The `setup.sh` script handles all of the above automatically!

#### 3. Frontend Setup
```bash
# In a new terminal, from project root
npm install
npm run dev
```

#### 4. Access Application
- **Frontend**: http://localhost:5173 (or 5174 if 5173 is busy)
- **Backend API**: http://localhost:8000
- **Health Check**: http://localhost:8000/health

## 🔧 Troubleshooting

### If Detection Results Differ Between Computers

**Problem**: Different detection results on different machines.

**Solution**: Ensure consistent environment setup:

```bash
# 1. Check code version
git log --oneline -3

# 2. Clean model cache
rm -rf ~/.cache/huggingface/
rm -rf __pycache__/

# 3. Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# 4. Restart services
python main.py
```

### If Models Fail to Load

**Problem**: RoBERTa or Zero-shot models fail to load.

**Solution**: This is normal - the system gracefully degrades:
- GPT-4 detection still works (primary model)
- CLIP model provides additional features
- System continues to function normally

### If API Errors Occur

**Problem**: 401 Unauthorized or API connection errors.

**Solution**: 
```bash
# Check API key
cat .env | grep OPENAI_API_KEY

# Verify service status
curl http://localhost:8000/health
```

## 📋 Features

- **Multi-Model Detection**: GPT-4, RoBERTa, CLIP, Zero-shot classification
- **Fact Verification**: Tavily API integration for real-time fact checking
- **Error Highlighting**: Visual highlighting of detected errors in text
- **Fake News Generation**: Controlled generation for research purposes
- **Comprehensive Analysis**: Detailed reports with confidence scores

## 🔑 API Keys

The `.env.example` file contains shared team API keys for immediate use:
- **OpenAI API**: For GPT-4 detection and generation
- **Tavily API**: For fact verification

**Note**: For production use, replace with your own API keys.

---

# React + TypeScript + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) (or [oxc](https://oxc.rs) when used in [rolldown-vite](https://vite.dev/guide/rolldown)) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the ESLint configuration

If you are developing a production application, we recommend updating the configuration to enable type-aware lint rules:

```js
export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...

      // Remove tseslint.configs.recommended and replace with this
      tseslint.configs.recommendedTypeChecked,
      // Alternatively, use this for stricter rules
      tseslint.configs.strictTypeChecked,
      // Optionally, add this for stylistic rules
      tseslint.configs.stylisticTypeChecked,

      // Other configs...
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```

You can also install [eslint-plugin-react-x](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-x) and [eslint-plugin-react-dom](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-dom) for React-specific lint rules:

```js
// eslint.config.js
import reactX from 'eslint-plugin-react-x'
import reactDom from 'eslint-plugin-react-dom'

export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...
      // Enable lint rules for React
      reactX.configs['recommended-typescript'],
      // Enable lint rules for React DOM
      reactDom.configs.recommended,
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```

**Important**: Create a `.env` file in the `backend/` directory with your API keys. The `.env.example` file provides a template.

### Using Shared Team API Keys

For team collaboration, you can use the shared API keys by copying them from the team documentation or contacting the project maintainer.

**Note**: Always keep your API keys secure and never commit them to the repository.
# Force Update Wed Oct 29 16:10:24 AEDT 2025
