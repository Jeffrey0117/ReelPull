# ReelPull

Instagram Reels 下載工具 - Web 版本

## 功能

- 批次下載 Instagram Reels 影片
- 即時進度顯示（WebSocket）
- 下載佇列管理
- 歷史紀錄
- Toast 通知系統
- 深色主題 UI

## 技術棧

### 後端
- FastAPI
- SQLite + SQLAlchemy
- Selenium + ChromeDriver
- WebSocket

### 前端
- Vue 3 + Vite
- 原生 CSS

## 快速開始

### 1. 安裝後端依賴

```bash
cd backend
pip install -r requirements.txt
```

### 2. 啟動後端

```bash
cd backend
python main.py
```

後端會在 http://localhost:8000 啟動
API 文檔：http://localhost:8000/docs

### 3. 安裝前端依賴

```bash
cd frontend
npm install
```

### 4. 啟動前端

```bash
cd frontend
npm run dev
```

前端會在 http://localhost:5173 啟動

## 專案結構

```
reelpull/
├── backend/
│   ├── main.py              # FastAPI 主程式
│   ├── schemas.py           # Pydantic 資料模型
│   ├── requirements.txt
│   ├── api/
│   │   ├── routes.py        # REST API 路由
│   │   └── websocket.py     # WebSocket 管理
│   ├── models/
│   │   └── database.py      # SQLite 模型
│   └── services/
│       └── downloader.py    # Selenium 下載邏輯
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

## API

| Method | Path | 說明 |
|--------|------|------|
| POST | /api/queue | 新增網址到佇列 |
| GET | /api/queue | 取得目前佇列 |
| DELETE | /api/queue/{id} | 刪除佇列項目 |
| POST | /api/queue/{id}/retry | 重試失敗項目 |
| GET | /api/history | 取得歷史紀錄 |
| DELETE | /api/history | 清除歷史 |
| GET | /api/settings | 取得設定 |
| PUT | /api/settings | 更新設定 |
| POST | /api/download/start | 開始下載 |
| POST | /api/download/stop | 停止下載 |
| GET | /api/download/status | 取得狀態 |

WebSocket: `ws://localhost:8000/ws`

## 使用方式

1. 開啟 http://localhost:5173
2. 貼上 Instagram Reel 網址（支援多行）
3. 點擊「加入佇列」
4. 點擊「開始下載」
5. 觀看即時進度

## 支援的網址格式

- `https://www.instagram.com/reel/xxxxx`
- `https://www.instagram.com/p/xxxxx`

## 設定

| 設定 | 說明 |
|------|------|
| 下載路徑 | 影片存放位置 |
| 無頭模式 | 隱藏瀏覽器視窗 |
| 自動移除 | 完成後從佇列移除 |

## License

MIT
