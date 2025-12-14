from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from models import Download, Setting, get_db
from schemas import UrlInput, DownloadResponse, SettingUpdate, SettingsResponse

router = APIRouter(prefix="/api", tags=["api"])


# ========== Queue Endpoints ==========

@router.post("/queue", response_model=List[DownloadResponse])
def add_to_queue(input: UrlInput, db: Session = Depends(get_db)):
    """新增網址到下載佇列"""
    added = []
    for url in input.urls:
        # 檢查是否已存在
        existing = db.query(Download).filter(
            Download.url == url,
            Download.status.in_(["pending", "processing"])
        ).first()
        if existing:
            continue

        download = Download(url=url, status="pending")
        db.add(download)
        db.commit()
        db.refresh(download)
        added.append(download)

    return added


@router.get("/queue", response_model=List[DownloadResponse])
def get_queue(db: Session = Depends(get_db)):
    """取得目前下載佇列"""
    return db.query(Download).filter(
        Download.status.in_(["pending", "processing"])
    ).order_by(Download.created_at.desc()).all()


@router.delete("/queue/{download_id}")
def remove_from_queue(download_id: str, db: Session = Depends(get_db)):
    """從佇列移除項目"""
    download = db.query(Download).filter(Download.id == download_id).first()
    if not download:
        raise HTTPException(status_code=404, detail="Download not found")

    db.delete(download)
    db.commit()
    return {"message": "Removed successfully"}


@router.post("/queue/{download_id}/retry", response_model=DownloadResponse)
def retry_download(download_id: str, db: Session = Depends(get_db)):
    """重試失敗的下載"""
    download = db.query(Download).filter(Download.id == download_id).first()
    if not download:
        raise HTTPException(status_code=404, detail="Download not found")

    download.status = "pending"
    download.error_message = None
    db.commit()
    db.refresh(download)
    return download


# ========== History Endpoints ==========

@router.get("/history", response_model=List[DownloadResponse])
def get_history(limit: int = 50, db: Session = Depends(get_db)):
    """取得下載歷史"""
    return db.query(Download).filter(
        Download.status.in_(["completed", "failed"])
    ).order_by(Download.completed_at.desc()).limit(limit).all()


@router.delete("/history")
def clear_history(db: Session = Depends(get_db)):
    """清除下載歷史"""
    db.query(Download).filter(
        Download.status.in_(["completed", "failed"])
    ).delete()
    db.commit()
    return {"message": "History cleared"}


# ========== Settings Endpoints ==========

@router.get("/settings", response_model=SettingsResponse)
def get_settings(db: Session = Depends(get_db)):
    """取得設定"""
    settings = {s.key: s.value for s in db.query(Setting).all()}
    return SettingsResponse(
        download_path=settings.get("download_path", "./downloads"),
        headless_mode=settings.get("headless_mode", "false") == "true",
        auto_remove=settings.get("auto_remove", "true") == "true",
        show_notification=settings.get("show_notification", "true") == "true"
    )


@router.put("/settings", response_model=SettingsResponse)
def update_settings(update: SettingUpdate, db: Session = Depends(get_db)):
    """更新設定"""
    updates = update.model_dump(exclude_none=True)

    for key, value in updates.items():
        setting = db.query(Setting).filter(Setting.key == key).first()
        str_value = str(value).lower() if isinstance(value, bool) else value
        if setting:
            setting.value = str_value
        else:
            db.add(Setting(key=key, value=str_value))

    db.commit()
    return get_settings(db)
