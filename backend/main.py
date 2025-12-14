from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio

from models import init_db
from api.routes import router
from api.websocket import manager
from services.downloader import download_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 啟動時初始化資料庫
    init_db()
    yield
    # 關閉時清理
    if download_service.driver:
        download_service.driver.quit()


app = FastAPI(
    title="ReelPull API",
    description="Instagram Reels 下載服務",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 設定 - 允許前端存取
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 註冊 API 路由
app.include_router(router)


# WebSocket 端點
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # 可以處理來自前端的訊息
            if data == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# 下載控制端點
@app.post("/api/download/start")
async def start_download():
    """開始下載佇列"""
    status = download_service.get_status()
    if status["is_running"]:
        return {"success": False, "message": "Already running", **status}

    # 在背景執行下載
    asyncio.create_task(download_service.start_downloads())
    return {"success": True, "message": "Download started", "status": "running"}


@app.post("/api/download/stop")
async def stop_download():
    """停止下載"""
    result = await download_service.stop_downloads()
    return result


@app.get("/api/download/status")
async def download_status():
    """取得下載服務詳細狀態"""
    return download_service.get_status()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
