# app/controllers/unload.py
from fastapi import APIRouter
from app.services.model_loader import model_loader

router = APIRouter()

@router.post("/unload")
def unload_model(source_lang: str, target_lang: str):
    key = f"{source_lang}-{target_lang}"
    result = model_loader.unload_model(source_lang, target_lang)
    if result:
        return {"message": f"Model {key} unloaded successfully"}
    else:
        return {"message": f"Model {key} was not loaded"}