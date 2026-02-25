# AGENTS.md

## Cursor Cloud specific instructions

### Architecture
- **Frontend**: React 19 + Vite 7 + TypeScript (port 5173). Uses npm as package manager.
- **Backend**: Python FastAPI + Uvicorn (port 8000). Dependencies via pip from `backend/requirements.txt`.
- **Database**: MongoDB 6.0 via Docker Compose (`backend/docker-compose.mongo.yml`). Default creds: `admin` / `admin123`, database: `fakenews_db`.
- Vite proxies `/api` and `/health` requests to the backend on port 8000 (see `vite.config.ts`).

### Running services
1. **MongoDB**: `sudo dockerd &>/dev/null &` then `sudo docker compose -f backend/docker-compose.mongo.yml up -d` from `/workspace/backend`.
2. **Backend**: `cd /workspace/backend && python3 main.py` (runs on port 8000). Creates `logs/` directory automatically. First run downloads HuggingFace models (~2GB total: RoBERTa, CLIP, zero-shot).
3. **Frontend**: `npm run dev` from `/workspace` (runs on port 5173).

### Key caveats
- `requirements.txt` pins `numpy==1.24.3` and `spacy==3.7.0` which are incompatible with Python 3.12. Install with relaxed version constraints (`>=` instead of `==`) for numpy, pillow, scikit-learn, and spacy.
- After installing Python deps, run `python3 -m spacy download en_core_web_sm` and download NLTK data (`punkt`, `punkt_tab`, `stopwords`, `averaged_perceptron_tagger`, `averaged_perceptron_tagger_eng`).
- The `OPENAI_API_KEY` environment variable is required for GPT-4o detection/generation features. Without it, the backend starts but those features return errors. The ML models (RoBERTa, CLIP, zero-shot) still work without it.
- ESLint (`npm run lint`) reports ~66 pre-existing errors (mostly `@typescript-eslint/no-explicit-any`). TypeScript (`tsc -b`) also has pre-existing errors. These are in the original code.
- Docker is needed for MongoDB. The environment requires `fuse-overlayfs` and `iptables-legacy` for nested Docker-in-Docker support.
- `pip install --user` is needed since system site-packages is not writable. Ensure `$HOME/.local/bin` is on PATH for executables like `uvicorn` and `spacy`.

### Standard commands
- See `package.json` scripts for frontend: `npm run dev`, `npm run build`, `npm run lint`, `npm run test`.
- Backend start: `python3 main.py` from `/workspace/backend`.
- Backend tests: `python3 -m pytest backend/tests/ -q` from `/workspace`.
