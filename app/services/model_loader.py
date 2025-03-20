# app/services/model_loader.py
import asyncio
import logging
from collections import OrderedDict
import os
from datetime import datetime
from app.config import config
from app.services.marian_runtime import MarianRuntime

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
        
        logging.info(f"Loading model {key}")

        async with self.load_semaphore:
            # Offload blocking model load to a thread
            model_dir = os.path.join("app", "models", key)
            if not os.path.exists(model_dir):
                logging.error(f"Model directory not found: {model_dir}")
                raise FileNotFoundError(f"Model directory not found: {model_dir}")
            
            # Create runtime
            runtime = MarianRuntime(model_dir)
            
            # Initialize runtime (this will validate the model files)
            try:
                await runtime.start()
                logging.info(f"Model {key} loaded successfully")
            except Exception as e:
                logging.error(f"Failed to load model {key}: {str(e)}")
                raise

            if len(self.models) >= self.cache_size:
                oldest_key = next(iter(self.models))  # Get just the first key
                oldest_runtime = self.models.pop(oldest_key)
                logging.info(f"Cache full, unloading model {oldest_key}")
                await oldest_runtime.stop()
            
            # Add to cache
            self.models[key] = runtime
            return runtime
    
    async def unload_model(self, src: str, tgt: str):
        """Unload a model from cache"""
        key = self._make_model_key(src, tgt)
        if key in self.models:
            runtime = self.models.pop(key)
            await runtime.stop()
            logging.info(f"Model {key} unloaded")
            return True
        return False
    
    async def clear_cache(self):
        """Clear all models from cache"""
        for key, runtime in self.models.items():
            logging.info(f"Stopping model {key}")
            await runtime.stop()
        
        self.models.clear()
        logging.info("Model cache cleared")

    def get_status(self):
        """Get status of loaded models"""
        return [
            {
                "model_key": key,
                "source_lang": key.split("-")[0],
                "target_lang": key.split("-")[1],
                "loaded_at": datetime.now().isoformat() if hasattr(runtime, "loaded_at") else None
            }
            for key, runtime in reversed(self.models.items())
        ]
    
    
model_loader = ModelLoader()
    