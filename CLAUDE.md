# ReelPull

Instagram Reels batch downloader. FastAPI + Selenium backend, Vue 3 frontend, real-time progress via WebSocket. A core component of [AutoReel](https://github.com/Jeffrey0117/AutoReel).

## Stack
- **Backend**: Python 3.10+, FastAPI, Uvicorn, SQLAlchemy 2.0 + SQLite (`reelpull.db`), Pydantic v2
- **Scraping**: Selenium + ChromeDriver (managed via webdriver-manager), requires Google Chrome
- **Frontend**: Vue 3 + Vite 5, native CSS (no UI framework)
- **Realtime**: WebSocket (`/ws`) for live download status
- **Aux server**: standalone Express 5 static/video file server in `backend/downloads/`

## Directory structure

```
backend/
  main.py            ← FastAPI entry: app, CORS, lifespan, /ws + /api/download/* endpoints
  schemas.py         ← Pydantic request/response models
  requirements.txt
  api/
    routes.py        ← REST routes (queue, history, settings)
    websocket.py     ← ConnectionManager (broadcasts progress)
  models/
    database.py      ← SQLAlchemy engine, Download + Setting models, init_db()
  services/
    downloader.py    ← DownloadService: Selenium driver, download loop, status/stats
  downloads/         ← Saved .mp4 output + separate Express viewer (server.js, public/)
frontend/
  vite.config.js     ← multi-page (index/videos/landing), dev proxy /api + /ws → :8000
  index.html, videos.html, landing.html
  src/
    main.js, App.vue           ← main download UI
    videos-main.js, Videos.vue ← download history/library view
    api/index.js               ← API client
    style.css, videos.css
docs/
  README_zh-TW.md, SAAS_BUSINESS_PLAN.md
```

## Key concepts

- **Entry points**: backend `python main.py` (Uvicorn on :8000, `reload=True`); frontend `npm run dev` (Vite on :5173).
- **Download flow**: `POST /api/queue` enqueues URLs → `POST /api/download/start` spawns an asyncio background task running `DownloadService.start_downloads()` → Selenium scrapes each Reel → progress broadcast over WebSocket → rows persisted in `downloads` table.
- **Single-run guard**: `_download_task` tracked in `main.py`; start is rejected if `is_running`. Task cancelled and driver `.quit()` on app shutdown (lifespan).
- **Data model**: `Download` (id/url/status/filename/error_message/timestamps; status = pending|processing|completed|failed) and `Setting` (key/value). Defaults seeded in `init_db()`: download_path, headless_mode, auto_remove, show_notification.
- **Settings** drive runtime behavior: download path, headless Chrome, auto-remove completed items.
- **CORS** restricted to `localhost:5173` / `127.0.0.1:5173`. Vite dev server also proxies `/api` and `/ws` to :8000.
- **Supported URLs**: `instagram.com/reel/...` and `instagram.com/p/...`.
- **API docs**: auto-generated at `http://localhost:8000/docs`.

## Commands

Backend (run from `backend/`):
- `pip install -r requirements.txt` — install deps
- `python main.py` — run API (http://localhost:8000)

Frontend (run from `frontend/`):
- `npm install` — install deps
- `npm run dev` — dev server (http://localhost:5173)
- `npm run build` — production build (multi-page)
- `npm run preview` — preview built output

Aux video viewer (run from `backend/downloads/`):
- `npm install && node server.js` — Express file server on :3000

## API reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/queue` | Add URLs to queue |
| GET | `/api/queue` | Get current queue |
| DELETE | `/api/queue/{id}` | Remove queue item |
| POST | `/api/queue/{id}/retry` | Retry failed item |
| GET | `/api/history` | Get download history |
| DELETE | `/api/history` | Clear history |
| GET / PUT | `/api/settings` | Get / update settings |
| POST | `/api/download/start` | Start downloading |
| POST | `/api/download/stop` | Stop downloading |
| GET | `/api/download/status` | Download service status |
| WS | `/ws` | Live progress (`ping` → `pong`) |

## Coding rules

- Backend code comments and user-facing messages are written in Traditional Chinese; keep that convention.
- No test suite is configured. Verify changes manually via the running app and `/docs`.
