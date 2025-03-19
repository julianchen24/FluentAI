# app/controllers/load.py
from fastapi import APIRouter, HTTPException
from app.services.model_loader import model_loader

router = APIRouter()

@router.post("/load")
async def load_model(source_lang: str, target_lang: str):
    key = f"{source_lang}-{target_lang}"
    if key in model_loader.models:
        raise HTTPException(status_code=400, detail="Model already loaded")
    try:
        await model_loader.load_model(source_lang, target_lang)
        return {"message": f"Model {key} loaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
