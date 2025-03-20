# app/controllers/translate.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.translation import translate_text
from app.config import config

router = APIRouter()

class TranslationRequest(BaseModel):
    source_lang: str
    target_lang: str
    text: str

@router.post("/translate")
async def translate(request: TranslationRequest):

    supported_langs = config.get("supported_languages", [])
    if request.source_lang not in supported_langs:
        raise HTTPException(status_code=400, detail=f"Source language '{request.source_lang}' not supported")
    
    if request.target_lang not in supported_langs:
        raise HTTPException(status_code=400, detail=f"Target language '{request.target_lang}' not supported")
    
    try:
        result = await translate_text(request.source_lang, request.target_lang, request.text)
        return {"translated_text": result}
    
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")