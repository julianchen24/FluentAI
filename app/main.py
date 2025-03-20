# venv\Scripts\Activate.ps1
# docker pull intel/nmt_marian_framework_demo
# docker run -it intel/nmt_marian_framework_demo


# app/main.py
from fastapi import FastAPI
from app.controllers import translate, load, unload, clear, status
from app.config import config
from app.utils.errors import http_error_handler

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
    import uvicorn
    uvicorn.run(app, host=config.get("host", "0.0.0.0"), port=config.get("port", 8000))
