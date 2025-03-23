# app/utils/errors.py
from fastapi import Request
from fastapi.responses import JSONResponse
from datetime import datetime

async def http_error_handler(request: Request, exc):
    status_code = getattr(exc, "status_code", 500)
    message = getattr(exc, "detail", str(exc))
    
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "error",
            "error": exc.__class__.__name__,
            "message": message,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    )