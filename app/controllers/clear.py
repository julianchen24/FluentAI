# app/controllers/clear.py
from fastapi import APIRouter
from app.services.model_loader import model_loader

router = APIRouter()

@router.post("/clear")
def clear_cache():
    model_loader.clear_cache()
    return {"message": "Model cache cleared"}
