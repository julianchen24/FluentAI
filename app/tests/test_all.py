# tests/test_all.py
import pytest
from fastapi.testclient import TestClient

from app.main import app
client = TestClient(app)

def test_translate_direct():
    # Test a direct translation where one of the languages is the pivot.
    response = client.post("/translate", json={
        "source_lang": "en",
        "target_lang": "fr",
        "text": "Hello, world!"
    })
    assert response.status_code == 200
    data = response.json()
    assert "translated_text" in data
    # You can add more assertions if you know the expected output

def test_translate_pivot():
    # Test a pivot translation (e.g., Spanish to French via English).
    response = client.post("/translate", json={
        "source_lang": "es",
        "target_lang": "fr",
        "text": "Hola, mundo!"
    })
    assert response.status_code == 200
    data = response.json()
    assert "translated_text" in data

def test_status_and_clear():
    # Test the status endpoint after loading a model,
    # then clear the cache and verify the message.
    
    # Load a model (adjust parameters as needed for your environment)
    load_response = client.post("/load", params={"source_lang": "en", "target_lang": "fr"})
    # Status endpoint should show the loaded model
    status_response = client.get("/status")
    assert status_response.status_code == 200
    status_data = status_response.json()
    assert "loaded_models" in status_data
    assert len(status_data["loaded_models"]) > 0

    # Now clear the cache
    clear_response = client.post("/clear")
    assert clear_response.status_code == 200
    clear_data = clear_response.json()
    assert clear_data.get("message") == "Model cache cleared"

if __name__ == "__main__":
    pytest.main()
