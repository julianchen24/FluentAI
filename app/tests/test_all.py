# app/tests/test_all.py
import pytest
from fastapi.testclient import TestClient
import os
import sys
from unittest.mock import AsyncMock, patch, MagicMock

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import app after adjusting the path
from app.main import app
from app.services.model_loader import model_loader

# Create test client
client = TestClient(app)

# Use this context manager to mock the model loading and translation
@pytest.fixture
def mock_translation():
    # Create a patched version of the model_loader
    with patch('app.services.translation.model_loader') as mock_loader, \
         patch('app.controllers.status.model_loader') as mock_status_loader, \
         patch('app.controllers.load.model_loader') as mock_load_loader, \
         patch('app.controllers.clear.model_loader') as mock_clear_loader, \
         patch('app.controllers.unload.model_loader') as mock_unload_loader:
        
        # Create a mock runtime
        mock_runtime = AsyncMock()
        mock_runtime.translate = AsyncMock(return_value="Translated text")
        mock_runtime.start = AsyncMock()
        mock_runtime.stop = AsyncMock()
        
        # Configure model_loader mock
        mock_loader.load_model = AsyncMock(return_value=mock_runtime)
        mock_loader.models = {}  # Start with empty models
        
        # Configure the status loader mock
        mock_status_loader.get_status = MagicMock(return_value=[
            {"model_key": "en-es", "source_lang": "en", "target_lang": "es", "loaded_at": "2024-03-23T10:00:00Z"}
        ])
        
        # Configure the clear loader mock
        mock_clear_loader.clear_cache = AsyncMock()
        
        # Configure the load loader mock
        mock_load_loader.load_model = AsyncMock()
        mock_load_loader.models = {}
        
        # Configure the unload loader mock
        mock_unload_loader.unload_model = AsyncMock(return_value=True)
        
        yield

# Test direct translation
def test_translate_direct(mock_translation):
    response = client.post("/translate", json={
        "source_lang": "en",
        "target_lang": "fr",
        "text": "Hello, world!"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "translated_text" in data
    assert data["translated_text"] == "Translated text"

# Test pivot translation
def test_translate_pivot(mock_translation):
    response = client.post("/translate", json={
        "source_lang": "es",
        "target_lang": "fr",
        "text": "Hola, mundo!"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "translated_text" in data
    assert data["translated_text"] == "Translated text"

# Test status endpoint
def test_status(mock_translation):
    response = client.get("/status")
    
    assert response.status_code == 200
    data = response.json()
    assert "loaded_models" in data
    assert len(data["loaded_models"]) > 0
    assert data["loaded_models"][0]["model_key"] == "en-es"

# Test load model endpoint
def test_load(mock_translation):
    response = client.post("/load", params={"source_lang": "en", "target_lang": "fr"})
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "loaded successfully" in data["message"]

# Test unload model endpoint
def test_unload(mock_translation):
    response = client.post("/unload", params={"source_lang": "en", "target_lang": "fr"})
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "unloaded successfully" in data["message"]

# Test clear cache endpoint
def test_clear(mock_translation):
    response = client.post("/clear")
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["message"] == "Model cache cleared"

# Test unsupported language
def test_unsupported_language():
    response = client.post("/translate", json={
        "source_lang": "xx",  # This language code doesn't exist
        "target_lang": "fr",
        "text": "Hello, world!"
    })
    
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data  # FastAPI returns errors in "detail" field
    assert "not supported" in data["detail"]

if __name__ == "__main__":
    pytest.main()