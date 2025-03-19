# app/services/model_loader.py
import asyncio
from collections import OrderedDict
from transformers import MarianMTModel, MarianTokenizer
from app.config import config

class ModelLoader:
    def __init__(self, cache_size: int = config.get("cache_size",6)):
        self.cache_size = cache_size
        self.models = OrderedDict()  # key: "src-tgt" -> (model, tokenizer)
        self.load_semaphore = asyncio.Semaphore(5)

    def _make_model_key(self, src: str, tgt: str) -> str:
        return f"{src}-{tgt}"
    
    async def load_model(self, src: str, tgt: str):
        key = self._make_model_key(src, tgt)
        # Return from cache if already loaded
        if key in self.models:
            self.models.move_to_end(key)
            return self.models[key]
        
        async with self.load_semaphore:
            # Offload blocking model load to a thread
            loop = asyncio.get_event_loop()
            model, tokenizer = await loop.run_in_executor(None, self._load_model_sync, src, tgt)
            if len(self.models) >= self.cache_size:
                self.models.popitem(last=False)
            self.models[key] = (model, tokenizer)
            return model, tokenizer
        
    def _load_model_sync(self, src: str, tgt: str):
        model_name = f"Helsinki-NLP/opus-mt-{src}-{tgt}"
        model = MarianMTModel.from_pretrained(model_name)
        tokenizer = MarianTokenizer.from_pretrained(model_name)
        return model, tokenizer
    
    def unload_model(self, src: str, tgt: str):
        key = self._make_model_key(src, tgt)
        return self.models.pop(key, None)
    
    def clear_cache(self):
        self.models.clear()

    def get_status(self):
        return list(reversed(self.models.keys()))
    
model_loader = ModelLoader()
    