# app/services/translation.py
import asyncio
from app.services.model_loader import model_loader
from app.config import config
import logging

# ***** This might need to be changed later because we have no direct translations other than english" *****

async def translate_text(source_lang: str, target_lang: str, text: str) -> str:
    """
    Translate text from source language to target language.
    Uses pivot translation through pivot_lang if direct translation is not available.
    
    Returns a dictionary with translation results and metadata.
    """
    if source_lang == target_lang:
        return text

    pivot_lang = config.get("pivot_lang", "en")
    try:
        # Use direct translation if one of the languages is the pivot language
        if source_lang == pivot_lang or target_lang == pivot_lang:
            logging.info(f"Direct translation from {source_lang} to {target_lang}")
            runtime = await model_loader.load_model(source_lang, target_lang)
            return await runtime.translate(text)
        else:
            # For pivot translation: source -> pivot, then pivot -> target
            logging.info(f"Pivot translation from {source_lang} to {target_lang} via {pivot_lang}")
            
            # First translate to pivot language
            runtime1 = await model_loader.load_model(source_lang, pivot_lang)
            intermediate_text = await runtime1.translate(text)
            
            # Then translate to target language
            runtime2 = await model_loader.load_model(pivot_lang, target_lang)
            return await runtime2.translate(intermediate_text)
        
    except Exception as e:
        logging.error(f"Translation error: {str(e)}")
        raise
