# app/controllers/translate.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.translation import translate_text

router = APIRouter()

class TranslationRequest(BaseModel):
    source_lang: str
    target_lang: str
    text: str

@router.post("/translate")
async def translate(request: TranslationRequest):
    try:
        result = await translate_text(request.source_lang, request.target_lang, request.text)
        return {"translated_text": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

