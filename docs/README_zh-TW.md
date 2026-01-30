<div align="center">

# ReelPull

**批次下載 Instagram Reels，即時追蹤下載進度。**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](../LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://python.org)
[![Vue](https://img.shields.io/badge/Vue-3-4FC08D?logo=vuedotjs&logoColor=white)](https://vuejs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)

[English](../README.md) | 繁體中文

</div>

---

## 功能

- **批次下載** — 一次加入多個 Instagram Reels 網址，批次下載
- **即時進度** — 透過 WebSocket 即時更新下載狀態
- **佇列管理** — 新增、移除、重試下載項目
- **歷史紀錄** — 瀏覽與管理已下載的影片
- **Toast 通知** — 非侵入式狀態通知
- **深色主題** — 以 Vue 3 打造的現代深色介面

## 技術棧

| 層級 | 技術 |
|------|------|
| **後端** | FastAPI、SQLite + SQLAlchemy、Selenium + ChromeDriver、WebSocket |
| **前端** | Vue 3、Vite、原生 CSS |

## 快速開始

### 前置需求

- Python 3.10+
- Node.js 18+
- Google Chrome（供 Selenium 使用）

### 安裝

```bash
# 複製專案
git clone https://github.com/Jeffrey0117/reelpull.git
cd reelpull

# 後端
cd backend
pip install -r requirements.txt

# 前端
cd ../frontend
npm install
```

### 啟動

```bash
# 啟動後端 (http://localhost:8000)
cd backend
python main.py

# 啟動前端 (http://localhost:5173)
cd frontend
npm run dev
```

> API 文件：[http://localhost:8000/docs](http://localhost:8000/docs)

## 使用方式

1. 開啟 [http://localhost:5173](http://localhost:5173)
2. 貼上一個或多個 Instagram Reel 網址（每行一個）
3. 點擊 **加入佇列**
4. 點擊 **開始下載**
5. 即時查看下載進度

### 支援的網址格式

```
https://www.instagram.com/reel/xxxxx
https://www.instagram.com/p/xxxxx
```

## API 參考

| 方法 | 端點 | 說明 |
|------|------|------|
| `POST` | `/api/queue` | 新增網址到佇列 |
| `GET` | `/api/queue` | 取得目前佇列 |
| `DELETE` | `/api/queue/{id}` | 刪除佇列項目 |
| `POST` | `/api/queue/{id}/retry` | 重試失敗項目 |
| `GET` | `/api/history` | 取得歷史紀錄 |
| `DELETE` | `/api/history` | 清除歷史 |
| `GET` | `/api/settings` | 取得設定 |
| `PUT` | `/api/settings` | 更新設定 |
| `POST` | `/api/download/start` | 開始下載 |
| `POST` | `/api/download/stop` | 停止下載 |
| `GET` | `/api/download/status` | 取得狀態 |

**WebSocket：** `ws://localhost:8000/ws`

## 設定

| 設定項目 | 說明 |
|----------|------|
| 下載路徑 | 影片存放目錄 |
| 無頭模式 | 隱藏瀏覽器視窗執行 |
| 自動移除 | 下載完成後從佇列移除 |

## 專案結構

```
reelpull/
├── backend/
│   ├── main.py                # FastAPI 主程式
│   ├── schemas.py             # Pydantic 資料模型
│   ├── requirements.txt
│   ├── api/
│   │   ├── routes.py          # REST API 路由
│   │   └── websocket.py       # WebSocket 管理
│   ├── models/
│   │   └── database.py        # SQLite 模型
│   └── services/
│       └── downloader.py      # Selenium 下載邏輯
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

## 授權

[MIT](../LICENSE)
