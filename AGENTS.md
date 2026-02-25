# AGENTS.md

## Cursor Cloud specific instructions

### Architecture overview
Two-tier app: React/Vite SPA (root) + Python/FastAPI backend (`backend/`). MongoDB via Docker Compose. See `README.md` for full details.

### Services

| Service | Port | Start command |
|---------|------|---------------|
| Frontend (Vite) | 5173 | `npm run dev` (from repo root) |
| Backend (FastAPI) | 8000 | `cd backend && python3 main.py` |
| MongoDB | 27017 | `cd backend && sudo docker compose -f docker-compose.mongo.yml up -d` |

The Vite dev server proxies `/api/*` and `/health` to `http://localhost:8000` (configured in `vite.config.ts`).

### Running tests
- **Frontend**: `npm run test` (Vitest + React Testing Library)
- **Backend**: `cd backend && python3 -m pytest tests/ -v`
- **Lint**: `npm run lint` (ESLint)

### Gotchas
- **Python 3.12 compatibility**: `requirements.txt` pins `numpy==1.24.3` and `pillow==10.0.1` which don't compile on Python 3.12+. Install with relaxed versions: `pip3 install --user "numpy>=1.24,<2" "pillow>=10.0"` before the rest of requirements.
- **Case-sensitive imports on Linux**: `src/components/earth/Earth.tsx` shader imports use lowercase `earth` path to match the actual folder name. On macOS (case-insensitive FS) this is invisible; on Linux it breaks.
- **Docker in Docker**: This cloud environment requires `fuse-overlayfs` storage driver and `iptables-legacy` for Docker to work. See the Docker setup section in the system instructions.
- **MongoDB credentials**: Default Docker Compose uses `admin`/`admin123`. The backend config auto-constructs the connection string from these defaults.
- **OpenAI API key is optional for startup**: The backend starts and serves detection results from local ML models (zero-shot, RoBERTa, CLIP) even without an OpenAI key. GPT-4 features degrade gracefully.
- **Backend .env location**: Must be at `backend/.env`, not root `.env`. Root `.env` is for Vite/Firebase frontend variables.
- **ML model downloads on first run**: The backend downloads HuggingFace models (RoBERTa, CLIP, BART-MNLI) on first startup, which can take 1-2 minutes.
