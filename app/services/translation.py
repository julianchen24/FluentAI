# app/services/translation.py
import asyncio
from app.services.model_loader import model_loader
from app.config import config

# ***** This might need to be changed later because we have no direct translations other than english" *****

async def translate_text(source_lang: str, target_lang: str, text: str) -> str:
    pivot_lang = config.get("pivot_lang", "en")

    # Use direct translation if one of the languages is the pivot language
    if source_lang == pivot_lang or target_lang == pivot_lang:
        runtime = await model_loader.load_model(source_lang, target_lang)
        return await runtime.translate(text)
    
    else:
        # For pivot translation: source -> pivot, then pivot -> target.
        runtime1 = await model_loader.load_model(source_lang, pivot_lang)
        intermediate_text = await runtime1.translate(text)
        runtime2 = await model_loader.load_model(pivot_lang, target_lang)
        return await runtime2.translate(intermediate_text)