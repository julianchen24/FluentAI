# app/controllers/clear.py
from fastapi import APIRouter
from app.services.model_loader import model_loader

router = APIRouter()

@router.post("/clear")
async def clear_cache():
    # Changed to async to match the async clear_cache method in model_loader
    await model_loader.clear_cache()
    return {"message": "Model cache cleared"}