<div align="center">

# ReelPull

**Save Instagram Reels. Fast and simple.**

A core component of [AutoReel](https://github.com/Jeffrey0117/video-translate-project).

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://python.org)
[![Vue](https://img.shields.io/badge/Vue-3-4FC08D?logo=vuedotjs&logoColor=white)](https://vuejs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)

[English](#features) | [繁體中文](docs/README_zh-TW.md)

</div>

---

## Features

- **Batch Download** — Queue multiple Instagram Reels and download them all at once
- **Real-time Progress** — Live status updates via WebSocket
- **Queue Management** — Add, remove, and retry downloads
- **Download History** — Browse and manage previously downloaded videos
- **Toast Notifications** — Non-intrusive status alerts
- **Dark Theme UI** — Modern dark interface built with Vue 3

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | FastAPI, SQLite + SQLAlchemy, Selenium + ChromeDriver, WebSocket |
| **Frontend** | Vue 3, Vite, Native CSS |

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- Google Chrome (for Selenium)

### Installation

```bash
# Clone the repository
git clone https://github.com/Jeffrey0117/reelpull.git
cd reelpull

# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install
```

### Running

```bash
# Start the backend (http://localhost:8000)
cd backend
python main.py

# Start the frontend (http://localhost:5173)
cd frontend
npm run dev
```

> API docs available at [http://localhost:8000/docs](http://localhost:8000/docs)

## Usage

1. Open [http://localhost:5173](http://localhost:5173)
2. Paste one or more Instagram Reel URLs (one per line)
3. Click **Add to Queue**
4. Click **Start Download**
5. Monitor real-time progress

### Supported URL Formats

```
https://www.instagram.com/reel/xxxxx
https://www.instagram.com/p/xxxxx
```

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/queue` | Add URLs to queue |
| `GET` | `/api/queue` | Get current queue |
| `DELETE` | `/api/queue/{id}` | Remove queue item |
| `POST` | `/api/queue/{id}/retry` | Retry failed item |
| `GET` | `/api/history` | Get download history |
| `DELETE` | `/api/history` | Clear history |
| `GET` | `/api/settings` | Get settings |
| `PUT` | `/api/settings` | Update settings |
| `POST` | `/api/download/start` | Start downloading |
| `POST` | `/api/download/stop` | Stop downloading |
| `GET` | `/api/download/status` | Get download status |

**WebSocket:** `ws://localhost:8000/ws`

## Configuration

| Setting | Description |
|---------|-------------|
| Download Path | Directory where videos are saved |
| Headless Mode | Run browser without visible window |
| Auto Remove | Remove items from queue after completion |

## Project Structure

```
reelpull/
├── backend/
│   ├── main.py                # FastAPI entry point
│   ├── schemas.py             # Pydantic models
│   ├── requirements.txt
│   ├── api/
│   │   ├── routes.py          # REST API routes
│   │   └── websocket.py       # WebSocket handler
│   ├── models/
│   │   └── database.py        # SQLite models
│   └── services/
│       └── downloader.py      # Selenium download logic
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   └── src/
│       ├── main.js
│       ├── App.vue
│       ├── style.css
│       └── api/index.js
└── README.md
```

## License

[MIT](LICENSE)
