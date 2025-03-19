# app/services/translation.py
import asyncio
from app.services.model_loader import model_loader
from app.config import config

# ***** This might need to be changed later because we have no direct translations other than english" *****

async def translate_text(source_lang: str, target_lang: str, text: str) -> str:
    pivot_lang = config.get("pivot_lang", "en")

    # Use direct translation if one of the languages is the pivot language
    if source_lang == pivot_lang or target_lang == pivot_lang:
        model, tokenizer = await model_loader.load_model(source_lang, target_lang)
        return await run_translation(model, tokenizer, text)
    
    else:
        # Pivot translation: source -> pivot, then pivot -> target
        model1, tokenizer1 = await model_loader.load_model(source_lang, pivot_lang)
        intermediate_text = await run_translation(model1, tokenizer1, text)
        model2, tokenizer2 = await model_loader.load_model(pivot_lang, target_lang)
        return await run_translation(model2, tokenizer2, intermediate_text)

async def run_translation(model, tokenizer, text: str) -> str:
    loop = asyncio.get_event_loop()
    translated = await loop.run_in_executor(None, _translate_sync, model, tokenizer, text)
    return translated

def _translate_sync(model, tokenizer, text: str) -> str:
    inputs = tokenizer(text, return_tensors="pt", padding=True)
    translated_tokens = model.generate(**inputs)
    translated_text = tokenizer.decode(translated_tokens[0], skip_special_tokens=True)
    return translated_text