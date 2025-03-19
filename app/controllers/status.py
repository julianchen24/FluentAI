# app/controllers/status.py
from fastapi import APIRouter
from app.services.model_loader import model_loader

router = APIRouter()

@router.get("/status")
def status():
    loaded_models = model_loader.get_status()
    return {"loaded_models": loaded_models}
