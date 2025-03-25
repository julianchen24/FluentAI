# (Don't really use this anymore) venv\Scripts\Activate.ps1
# ** in WSL source venv/bin/activate
# uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
# docker pull intel/nmt_marian_framework_demo
# docker run -it intel/nmt_marian_framework_demo

# python debug_marian.py en fr "I like to eat applesauce"
#marian_runtime.py
#main.py
#debug_marian.py

# app/main.py
from fastapi import FastAPI
from app.controllers import translate, load, unload, clear, status
from app.config import config
from app.utils.errors import http_error_handler
import logging

app = FastAPI(title="FluentAI")

# Register API routers
app.include_router(translate.router)
app.include_router(load.router)
app.include_router(unload.router)
app.include_router(clear.router)
app.include_router(status.router)

# Global exception handler for consistent error responses
app.add_exception_handler(Exception, http_error_handler)

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
    level=getattr(logging, config.get("log_level", "INFO")),
    filename=config.get("log_file", "fluentai.log"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(config.get("log_file", "fluentai.log")),
        logging.StreamHandler()  # Added this to see logs in console
    ]
)
    
    import uvicorn
    uvicorn.run(app, host=config.get("host", "0.0.0.0"), port=config.get("port", 8000))
